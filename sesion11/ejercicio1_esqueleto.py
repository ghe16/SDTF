import os
import json
import random

# Archivo del log de transacciones
WAL_FILE = "wal_log.json"
DB_FILE = "database.json"

class MiniWAL:
    def __init__(self):
        self.transactions = []
        self.load_database()

    def load_database(self):
        """Carga el estado de la base de datos desde el archivo"""
        #To do#
       

    def log_transaction(self, operation, amount):
        """Guarda la transacción en el WAL antes de aplicarla"""
        transaction = {"operation": operation, "amount": amount}
        self.transactions.append(transaction)
         #To do#
        

    def write_log(self):
        """Escribe las transacciones en el WAL"""
        with open(WAL_FILE, "w") as f:
            json.dump(self.transactions, f)

    def apply_transactions(self):
        """Aplica las transacciones registradas en el WAL a la base de datos. Las transacciones son deposit y withdraw sobre el total que es balance"""
         #To do#

        self.save_database()
        

    def save_database(self):
        """Guarda el estado actualizado de la base de datos"""
         #To do#

    def clear_log(self):
        """Elimina el WAL después de aplicar todas las transacciones"""
        self.transactions = []
        if os.path.exists(WAL_FILE):
            os.remove(WAL_FILE)

    def recover_from_log(self):
        """Recupera las transacciones pendientes del WAL tras un fallo"""
        if os.path.exists(WAL_FILE):
            with open(WAL_FILE, "r") as f:
                self.transactions = json.load(f)
            print(f"Recuperando {len(self.transactions)} transacciones del WAL...")
            self.apply_transactions()

# Simulación de uso
if __name__ == "__main__":
    wal = MiniWAL()

    # Simulamos transacciones antes de un posible fallo
    if random.randint(0, 1) == 1:
        wal.log_transaction("deposit", 100)
    else:
        wal.log_transaction("withdraw", 50)
    
    # Simular fallo antes de aplicar las transacciones
    print("Sistema falló antes de aplicar las transacciones...")

    # Reiniciar el sistema y recuperar desde WAL
    wal_recovered = MiniWAL()
    wal_recovered.recover_from_log()

    # Mostrar balance final
    print(f"Balance final: {wal_recovered.database['balance']}")
    # Eliminar el archivo de la base de datos
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)