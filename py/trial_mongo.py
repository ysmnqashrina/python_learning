
from pymongo import MongoClient 
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri = os.getenv("MONGODB_ATLAS_CLUSTER_URI")

class DatabaseManager:
    def __init__(self, db_name='exampledb', connection_string=mongo_uri):
        self.client = MongoClient(connection_string)
        self.db = self.client[db_name]
        self.users_collection = self.db.users
        self.posts_collection = self.db.posts
        self.init_database()
        
    def init_database(self):
        """initialize database with collection and indexes"""
        #create unique index on email fieldfor users 
        self.users_collection.create_index("email", unique=True)
        #create index on user_id field for posts for better query performance
        self.posts_collection.create_index("user_id")

    def create_user(self, name, email, age):
        """ Create a new user"""
        try:
            user_doc = {
                "name": name,
                "email": email,
                "age": age,
                "created_at": datetime.now()                
            }
            result = self.users_collection.insert_one(user_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error: {e}")
            return None

    def create_post(self, user_id, title, content):
        """ Create a new post"""
        try: 
            #convert string user_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(user_id):
                user_object_id = ObjectId(user_id)
            else:
                user_object_id = user_id

            post_doc = {
                "user_id": user_object_id,
                "title": title,
                "content": content,
                "created_at": datetime.now()                
            }
            result = self.posts_collection.insert_one(post_doc)
            return str(result.inserted_id)
        except Exception as e:
            print (f"Error Creating post: {e}")
            return None
    
    def get_all_users(self):
        """ Get all users"""
        try:
            users = list(self.users_collection.find())
            #convert ObjectId to string for easier display
            for user in users:
                user['_id'] = str(user['_id'])
            return users
        except Exception as e:
            print(f"Error retrieving users: {e}")
            return []
        
    def get_all_posts(self):
        """ Get all posts"""
        try:
            posts = list(self.posts_collection.find())
            #convert ObjectId to string for easier display
            for post in posts:
                post['_id'] = str(post['_id'])
                post['user_id'] = str(post['user_id'])
            return posts
        except Exception as e:
            print(f"Error retrieving posts: {e}")
            return []
        
    def get_user_posts(self, user_id):
        """ Get posts by user"""
        try:
            #convert string user_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(user_id):
                user_object_id = ObjectId(user_id)
            else:
                user_object_id = user_id

            posts = list(self.posts_collection.find(
                {"user_id": user_object_id}
            ).sort("created_at", -1))

            #convert ObjectId to string for easier display
            for post in posts:
                post['_id'] = str(post['_id'])
                post['user_id'] = str(post['user_id'])

            return posts
        except Exception as e:
            print(f"Error retrieving posts: {e}")
            return []

    def update_user(self, user_id, name=None, email=None, age=None):
        """ Update user information"""
        try:
            #convert string user_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(user_id):
                user_object_id = ObjectId(user_id)
            else:
                user_object_id = user_id

            #update user's info in posts collection as well
            update_fields = {}
            if name is not None:
                update_fields["name"] = name
            if email is not None:
                update_fields["email"] = email
            if age is not None:
                update_fields["age"] = age

            if update_fields:
                self.posts_collection.update_many({"user_id": user_object_id}, {"$set": update_fields})

            #update user
            result = self.users_collection.update_one({"_id": user_object_id}, {"$set": update_fields})
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def update_post(self, post_id, title=None, content=None):
        """ Update post information"""
        try:
            #convert string post_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(post_id):
                post_object_id = ObjectId(post_id)
            else:
                post_object_id = post_id

            update_fields = {}
            if title is not None:
                update_fields["title"] = title
            if content is not None:
                update_fields["content"] = content
            if update_fields:
                result = self.posts_collection.update_one({"_id": post_object_id}, {"$set": update_fields})
                return result.modified_count > 0
        except Exception as e:
            print(f"Error updating post: {e}")
            return False
    
    def delete_user(self, user_id):
        """ Delete user and their posts"""
        try:
            #convert string user_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(user_id):
                user_object_id = ObjectId(user_id)
            else:
                user_object_id = user_id

            #delete user's posts first
            self.posts_collection.delete_many({"user_id": user_object_id})

            #Delete the user
            result = self.users_collection.delete_one({"_id": user_object_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
        
    def delete_post(self, post_id):
        """ Delete a specific post"""
        try:
            #convert string post_id to ObjectId if it is a valid ObjectId
            if ObjectId.is_valid(post_id):
                post_object_id = ObjectId(post_id)
            else:
                post_object_id = post_id

            result = self.posts_collection.delete_one({"_id": post_object_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting post: {e}")
            return False
        
    def close_connection(self):
        """ Close the MongoDB connection"""
        self.client.close()

def display_menu():
    """ Display the main menu"""
    print("\n" + "="*40)
    print("        DATABASE MANAGER")
    print("="*40)
    print("1. Create User")
    print("2. View All Users")
    print("3. Create Post")
    print("4. View All Posts")
    print("5. View User Posts")
    print("6. Update User")
    print("7. Update Post")
    print("8. Delete User")
    print("9. Delete Post")
    print("10. Exit")
    print("-"*40)

def main(): 
    """Main interactive CLI function"""
    try:
        db = DatabaseManager()
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Make sure MongoDB is running on localhost:27017")
        return

    while True:
        display_menu()
        choice = input("Enter your choice (1-10): ").strip()

        if choice == '1':
            print("\n--- Create New User ---")
            name = input("Enter name: ").strip()
            email = input("Enter email: ").strip()
            try:             
                age = int(input("Enter age: ").strip())
                user_id = db.create_user(name, email, age)
                if user_id:
                    print(f"YES! User created successfully with ID: {user_id}")
                else:
                    print("SORRY! Failed to create user.")
            except ValueError:                    
                print("Invalid age entered. Please enter a number")

        elif choice == '2':
            print("\n--- All Users ---")    
            users = db.get_all_users()
            if users:
                for user in users:
                    print(f"ID: {user['_id']} | Name: {user['name']} | Email: {user['email']} | Age: {user['age']}")
            else:
                print("No users found.")

        elif choice == '3':
            print("\n--- Create New Post ---")
            user_id = input("Enter user ID: ").strip()
            title = input("Enter post title: ").strip()
            content = input("Enter post content: ").strip()
            post_id = db.create_post(user_id, title, content)
            if post_id:
                print(f"YES! Post created successfully with ID: {post_id}")
            else:
                print("SORRY! Failed to create post")

        elif choice == '4':
            print("\n--- All Posts ---")    
            posts = db.get_all_posts()
            if posts:
                for post in posts:
                    print(f"ID: {post['_id']} | User ID: {post['user_id']} | Title: {post['title']} | Content: {post['content']}")
            else:
                print("No posts found.")
   
        elif choice == '5':
            print("\n--- View User Posts ---")
            user_id = input("Enter user ID: ").strip()
            posts = db.get_user_posts(user_id)
            if posts:
                for post in posts:
                    print(f"\nPost ID: {post['_id']}")
                    print(f"Title: {post['title']}")
                    print(f"Content: {post['content']}")
                    print(f"Created: {post['created_at']}")
                    print("-" * 30)
            else:
                print("No posts found for this user.")

        elif choice == '6':
            print("\n--- Update User ---")
            user_id = input("Enter user ID to update: ").strip()
            name = input("Enter new name (leave blank to keep current): ").strip()
            email = input("Enter new email (leave blank to keep current): ").strip()
            age = input("Enter new age (leave blank to keep current): ").strip()
            if db.update_user(user_id, name=name, email=email, age=age):
                print(f"User with ID {user_id} updated successfully.")
            else:
                print(f"Failed to update user with ID {user_id}.")
                                  
        elif choice == '7':
            print("\n--- Update Post ---")
            user_id = input("Enter user ID to update post: ").strip()
            post_id = input("Enter post ID to update: ").strip()
            title = input("Enter new title (leave blank to keep current): ").strip()
            content = input("Enter new content (leave blank to keep current): ").strip()
            if db.update_post(post_id, title=title, content=content):
                print(f"Post with ID {post_id} updated successfully.")
            else:
                print(f"Failed to update post with ID {post_id}.")
                     
        elif choice == '8':
            print("\n--- Delete User ---")
            user_id = input("Enter user ID to delete: ").strip()
            confirm = input (f"Are you sure you want to delete user with ID {user_id}? (y/n): ").strip().lower()
            if confirm == 'y':
                if db.delete_user(user_id):
                    print(f"User with ID {user_id} deleted successfully.")
                else:
                    print(f"Deletion cancelled.")
        
        elif choice == '9':
            print("\n--- Delete Post ---")
            post_id = input("Enter post ID to delete: ").strip()
            confirm = input (f"Are you sure you want to delete post with ID {post_id}? (y/n): ").strip().lower()
            if confirm == 'y':
                if db.delete_post(post_id):
                    print(f"Post with ID {post_id} deleted successfully.")
                else:
                    print(f"Deletion cancelled.")

        elif choice == "10":
            print("\nClosing database connection and exiting the application. Goodbye!")
            db.close_connection()
            print ("Goodbye")
            break

        else:
            print("NOPE! Invalid choice. Please enter a number between 1-10.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()                        
                         