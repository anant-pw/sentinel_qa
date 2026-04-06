import yaml
import os
import re
from core.ai_factory import AIFactory
from loguru import logger

class RequirementAnalyst:
    def __init__(self):
        # The Factory will now pull SambaNova based on your config.yaml
        self.llm = AIFactory.get_model()

    def generate_test_plan(self, requirement_text: str, filename: str):
        """
        Converts unstructured text into a structured YAML test plan.
        Includes environment awareness from config.yaml.
        """
        # 1. Load environment context from config
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        base_url = config.get("base_url")

        # 2. Architect the Prompt for SambaNova
        prompt = f"""
        You are a Senior QA Architect. Convert this requirement into a YAML test plan.
        
        REQUIREMENT: {requirement_text}
        
        STRICT SELECTOR GUIDELINES (OrangeHRM):
        - Username field: input[name="username"]
        - Password field: input[name="password"]
        - Login Button: button[type="submit"]
        - Dashboard Header: .oxd-topbar-header-breadcrumb
        
        STRICT RULES:
        1. The first step MUST be to navigate to: {base_url}
        2. Return ONLY the YAML. No introductory text. No markdown explanation.
        3. Use ONLY these keys: title, steps.
        4. Valid Actions: navigate, type, click, verify_text.
        
        FORMAT EXAMPLE:
        title: "Login Verification"
        steps:
          - action: "navigate"
            data: "{base_url}"
          - action: "type"
            selector: "input[name='username']"
            data: "Admin"
          - action: "type"
            selector: "input[name='password']"
            data: "admin123"
          - action: "click"
            selector: "button[type='submit']"
          - action: "verify_text"
            selector: ".oxd-topbar-header-breadcrumb"
            data: "Dashboard"
        """
        
        logger.info(f"🧠 Sending requirement to SambaNova for: {filename}")
        
        # 3. Invoke the AI
        response = self.llm.invoke(prompt)
        
        # 4. Handle AIMessage object vs String (SambaNova specific)
        raw_text = response.content if hasattr(response, 'content') else str(response)

        # 5. Self-Healing Cleanup: Remove markdown backticks if AI added them
        clean_yaml = re.sub(r'```yaml|```', '', raw_text).strip()
        
        # 6. Validation and Saving
        try:
            # Verify if it's valid YAML before saving
            parsed_data = yaml.safe_load(clean_yaml)
            
            output_path = f"data/test_plans/pending/{filename}.yaml"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, "w") as f:
                yaml.dump(parsed_data, f, default_flow_style=False)
                
            logger.success(f"✅ Test Plan successfully generated at: {output_path}")
            
        except yaml.YAMLError as e:
            logger.error(f"❌ AI hallucinated invalid YAML syntax: {e}")
            logger.debug(f"Raw Output: {clean_yaml}")

if __name__ == "__main__":
    # Pilot Execution Block
    analyst = RequirementAnalyst()
    draft = """
    User should be able to login with valid credentials. 
    Fields: username and password. 
    Action: Click submit. 
    Validation: User should see the Dashboard breadcrumb.
    """
    # This matches the method name called in your error report
    analyst.generate_test_plan(draft, "login_feature")