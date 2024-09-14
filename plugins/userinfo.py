import os
import platform
import getpass

class UserInfos:
    def get_user_info(self):
        user_info = {
            'Display Name': getpass.getuser(),  
            'Hostname': platform.node(),        
            'Username': os.getlogin(),           
        }
        
        return user_info

    def print_user_info(self):
        info = self.get_user_info()
        for key, value in info.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    user_info = UserInfos()
    user_info.print_user_info()
