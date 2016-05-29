class Users(object):
    def __init__(self):
        pass

    @staticmethod
    def get_all(filter):
        return [
            {
                "name": "Gast",
                "drinks": [
                    {
                        "name": "Mio Mate",
                        "count": 6
                    },
                    {
                        "name": "Krombacher",
                        "count": 3
                    },
                    {
                        "name": "Club Mate",
                        "count": 2
                    }                   
                ]
            }
        ]