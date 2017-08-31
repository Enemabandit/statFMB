#Class to handle alerts to be used by template macro alert
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


#cleans the user input, checking if it is an alias
#NOTE: this is done in 2 cycles jor eficiency reasons
def clear_str(word,list_to_check,dict_to_double_check):
    for entry in list_to_check:
        if word.lower() == entry.lower():
            return entry
    else:
        for entry in list_to_check:
            if is_alias(word,entry,dict_to_double_check):
                return entry
        else:
            return "invalid"

#checks if user input is an alias
def is_alias(word, possible_alias, alias_dict):
    if possible_alias in alias_dict:
        alias_list_filtered = alias_dict.get(possible_alias)
    else:
        return False

    for alias in alias_list_filtered:
        if word.lower() == alias.lower():
            return True
    else:
        return False

#checks if a string represents and integer
def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
