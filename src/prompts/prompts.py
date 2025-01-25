from dataclasses import dataclass

@dataclass
class Prompt:

    def prompt_main(self):

        prompt_text = """Please analyze the attached photo of the medicine. Provide the advantages and disadvantages of this medicine, and explain why a doctor
                        might prescribe this specific medicine. Ensure that your response is strictly limited to medical terms and does not include any other information."""

        return prompt_text
