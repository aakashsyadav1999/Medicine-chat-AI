from src.components import main_script


class FlowPipeline:
    def __init__(self):
        self.main_script = main_script.MainScript()

    def run(self):
        self.main_script.run()
        self.main_script.llm_call()




if __name__ == "__main__":
    flow_pipeline = FlowPipeline()
    flow_pipeline.run()
