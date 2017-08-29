class Alert():

    def __init__(self,category = "danger",title ="Erro",description = "erro desconhecido"):
        if category in ["success","info","waring","danger","none"]:
            self.category = category
        else:
            self.category = "warning"

        self.title = title
        self.description = description

    def to_dict(self):
        return {"category": self.category,
                "title": self.title,
                "description" : self.description,
        }
