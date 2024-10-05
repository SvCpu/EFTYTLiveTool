from basic import description

class default_description(description):
    def __init__(self):
        self.description = description.default_description()
