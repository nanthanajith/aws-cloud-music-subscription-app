import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("login")

STUDENT_ID = "s4149287"          
FIRST_NAME = "Ajithkumar"        
LAST_NAME = "Nagananthakumaran"

passwords = [
    "012345",
    "123456",
    "234567",
    "345678",
    "456789",
    "567890",
    "678901",
    "789012",
    "890123",
    "901234"
]

for i in range(10):
    item = {
        "email": f"{STUDENT_ID}{i}@student.rmit.edu.au",
        "user_name": f"{FIRST_NAME}{LAST_NAME}{i}",
        "password": passwords[i]
    }

    table.put_item(Item=item)
    print(f"Inserted: {item['email']}")

print("All login users inserted successfully.")