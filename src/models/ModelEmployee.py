from .entities.Employee import Employee

class ModelEmployee():

    @classmethod
    def get_by_dni(db, dni):
        try:
            cursor = db.cursor()
            
            sql = f"""SELECT * FROM employee
                    WHERE dni_em = '{dni}'"""
                        
            cursor.execute(sql)
                
            row = cursor.fetchone()
            if row != None:
                user = Employee(row[0], row[1], row[2], row[3], None, row[5])
                return user
            else:
                return None

        except Exception as e:
            raise Exception(e)
        pass