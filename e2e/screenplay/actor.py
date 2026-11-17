class Actor:
    def __init__(self, name: str):
        self.name = name
        self._abilities = {}

    @classmethod
    def named(cls, name: str) -> "Actor":
        return cls(name)

    def who_can(self, ability):
        self._abilities[type(ability)] = ability
        return self

    def ability_to(self, ability_type):
        return self._abilities[ability_type]

    def attempts_to(self, *tasks) -> None:
        for task in tasks:
            task.perform_as(self)

    def asks_for(self, question):
        return question.answered_by(self)
