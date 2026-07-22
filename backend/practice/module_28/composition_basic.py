class Engine:
    def start(self) -> str:
        return "engine started"

class Car:
    def __init__(self, engine: Engine):
        self.engine = engine

    def drive(self) -> str:
        return self.engine.start()

print(Car(Engine()).drive())
