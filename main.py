# This is a Terminal / CLI based application, where you can handle in a variety
# of ways NASA's Astronomy Picture of the Day or APOD for short, images through
# API calls. This application is able to store the images viewed, on a local
# database, and use a custom image viewer written in Python to see them again!
#
#
#
# Author: Nikolaos Fokos
# Version 1.0
# Date: 17-1-2024
#
#
#
# FUTURE FIXES
# TODO: verify if database exists or not
# TODO: if not manage to take actions
# TODO: dynamic time greeting
# TODO: first time launch api key request from user
# TODO: Search for something like the requested search.
# TODO: General code/interface polishing
# TODO: Don't update the database if the entry already exists
# TODO: Ask user for API Key and then store it in a seperate file
#
#
# Imports
import datetime
import multiprocessing
import os
import random
import sqlite3
import threading
import time
from io import BytesIO
from pathlib import Path
from tkinter import Label, Tk, filedialog

import requests
from PIL import Image, ImageTk
from sqlalchemy import null


#
# Server ping utility
#
def ping(api_key):
      # Check API integrity
      apod_url = f'https://api.nasa.gov/planetary/apod?api-key={api_key}'
      # Request for a response
      response = requests.get(apod_url)
      # Check the status code of the response
      if (response.status_code == 200):
            print("[INFO] The provided API key is valid.")
      elif (response.status_code == 403):
            print("[ERROR] The provided API key is invalid. Access forbidden (403)")
      else:
            print(f"[ERROR] Unexpected response. Status code: {response.status_code}")
      # Return the status code
      return response.status_code
#
# A custom image viewer
#
def image_viewer(image_location):
      # Open the image from the specified path
      image = Image.open(image_location)
      # Set a proper thumbnail to fit in the window
      image.thumbnail((800, 600))
      # Create a new window
      root = Tk()
      # Give a title to the new window
      root.title("Image Viewer")
      # Make it unresizable
      root.resizable(False, False)
      # Select a darker theme for the window
      root.configure(bg="#1e1e1e")
      # Convert the PIL image to Tkinter PhotoImage
      tk_image = ImageTk.PhotoImage(image)
      # Create a label
      label = Label(root, image=tk_image, bd=0, highlightthickness=0)
      label.pack()
      # Start the Tkinter event loop
      root.mainloop()
#
# Fetch the APOD data in a JSON format
#
def get_apod(api_key):
      # The API calls the following url
      url = f'https://api.nasa.gov/planetary/apod?api_key={api_key}'
      # Store the response
      response = requests.get(url)
      if (response.status_code == 200):
            # Return the JSON data
            return response.json()
      else:
            print(f"[ERROR] Unable to fetch APOD data. Status code: {response.status_code}")
#
# APOD data handling
#
def display_apod(apod_data):
      # Fetch the APOD data from the JSON and assign them to variables
      title = apod_data['title']
      explanation = apod_data['explanation']
      url = apod_data['url'] # Store the url of the image data

      # Diplay in the terminal the collected data
      print(f"Title: {title}")
      print(f"Explanation: {explanation}")

      # Store the image
      try:
            # Fetch the APOD image 
            image_response = requests.get(url)
            if (image_response.status_code == 200):
                  # Convert the contents of the responded image to a readable format
                  image = Image.open(BytesIO(image_response.content))
                  try:
                        # Show up image
                        image_viewer(image)
                        # Inform the user about the image
                        print("[INFO] Image opened successfully.")
                  except Exception as e:
                        print(f"[ERROR] Unable to display image.: {e}")
            else:
                  print(f"[ERROR] Unable to fetch APOD image. Status code: {image_response.status_code}")
      
      except Exception as e:
            print(f"[ERROR] Unable to receive response: {e}")
#
# Search for an entry (NEEDS MULTIPLE FIXES)
#
def search(search_request):
      # Tell cursor to execute a SEARCH query
      try:
            result = cursor.execute(f"SELECT * FROM entries WHERE title LIKE '{search_request}%'")
            # Try to retrieve image properties
            id, title, explanation, image_location, date = result.fetchone()
            # Display the information
            print(f"""\n[INFO] Entry found:
\nEntry ID: {id}
\nDate added: {date}
\nTitle: {title}
\nExplanation: {explanation}\n""")
            try:
                  # Show up image
                  image_viewer(image_location)
                  # Inform the user about the image
                  print("[INFO] Image opened successfully.")
            except Exception as e:
                  print(f"[ERROR] Unable to display image: {e}")
      except Exception as e:
            print(f"[ERROR] Unable to locate entry: {e}")
#
# Delete a specific entry
#
def delete(delete_request):
      # Delete an entry
      try:
            # Try to remove the spacified entry
            cursor.execute(f"DELETE FROM entries WHERE id={delete_request}")
            print("[INFO] Commiting changes...")
            # Commit chages
            database.commit()
            print("[INFO] Entry removal completed successfully.")
      except Exception as e:
            # Warn user with a relative message
            print(f"[ERROR] Unable to delete entry: {e}")
            print("[INFO] Reversing possible changes...")
            # Reverse possible changes caused by incomplete statement
            database.rollback()
#
# Sort the entries
#
def sort():
      pass
#
# List all entries
#
def list():
      # Store all entries
      entries = cursor.execute("SELECT id, title, date FROM entries")
      # Interface
      print("\nEntries: ")
      # List all available entries
      for entry in entries:
            # Print all entries
            print(f"    {entry[0]}      {entry[2]}      {entry[1]}")
#
# View the current APOD
#
def apod():
      # Try to fetch the API Key from a local txt file
      try:
            # Read the API from file
            api_request = open("NASA_API_KEY.txt", "rt")
            print("NASA_API_KEY Found!")
            # Convert the opened file as text
            api_key = api_request.read()
            # Close file
            api_request.close()
            # Utilize the api_key for apod data.
            apod_data = get_apod(api_key)
            # Send the APOD data to display if possible
            if (apod_data):
                  display_apod(apod_data)
            else:
                  print(f"[ERROR]: Unable to display APOD data: {apod_data}")
      
      except Exception as e:
            print(f"[ERROR] Unable to read NASA_API_KEY: {e}")
#
# View a specific entry
#
def view(view_request):
      # Seek he entry into the database
      try:
            result = cursor.execute(f"SELECT * FROM entries WHERE id={view_request}")
            # Try to retrieve image properties
            id, title, explanation, image_location, date = result.fetchone()
            # Display the information
            print(f"""\n[INFO] Entry found:
\nEntry ID: {id}
\nDate added: {date}
\nTitle: {title}
\nExplanation: {explanation}\n""")
            try:
                  # Show up image
                  image_viewer(image_location)
                  # Inform the user about the image
                  print("[INFO] Image opened successfully.")
            except Exception as e:
                  print(f"[ERROR] Unable to display image: {e}")
      except Exception as e:
            print(f"[ERROR] Unable to view entry: {e}")
#
# Clear the terminal
#
def clear():
      # Clear the terminal
      os.system("cls")
#
# Update the database
#
def update():
      # Try to fetch the API Key from a local txt file
      try:
            print("[INFO] Updating database...")
            # Read the API from file
            api_request = open("NASA_API_KEY.txt", "rt")
            print("[INFO] NASA_API_KEY Found.")
            # Convert the opened file as text
            api_key = api_request.read()
            # Close file
            api_request.close()
            # Utilize the api_key for apod data.
            apod_data = get_apod(api_key)
            # Send the APOD data to display if possible
            if (apod_data):
                  # Fetch the APOD data from the JSON and assign them to variables
                  while (True):
                        # Assign random ID number to entry
                        id = random.randint(0, 1000) # Missing conflict checks
                        # Search for it in the database
                        id_conflict = cursor.execute(f"SELECT id FROM entries WHERE id={id}")
                        # Check if there is ID conflict
                        if (id_conflict.fetchone()):
                              # Continue to generate a random number
                              continue
                        else:
                              # If not break the loop
                              break
                  title = apod_data['title']
                  explanation = apod_data['explanation']
                  url = apod_data['url'] # Store the url of the image data
                  date = datetime.datetime.now().strftime("%d/%m/%Y - %X")
                  # Store the image
                  try:
                        # Fetch the APOD image
                        image_response = requests.get(url)
                        if (image_response.status_code == 200):
                              # Convert the contents of the responded image to a readable format
                              image = Image.open(BytesIO(image_response.content))
                              
                              ### Saving Procedure ###
                              # Create a new empty image
                              new_image = Image.new('RGB', (image.width, image.height), color = 'white')
                              # Paste the APOD image onto the new empty canvas
                              new_image.paste(image, (0, 0))
                              # Define the HOME directory of the user
                              home_directory = os.path.expanduser("~")
                              # Define the Pictures directory of the user
                              apod_directory = os.path.join(home_directory, 'Pictures', 'Space', 'APOD')
                              # Create it if not exist
                              os.makedirs(apod_directory, exist_ok = True)
                              # Name the new image after it's title
                              new_image_filename = f"{title}.png"
                              # Forge the new directory of the APOD folder and the filename
                              new_image_path = os.path.join(apod_directory, new_image_filename)
                              # Convert to Path
                              new_image_path = Path(new_image_path)
                              # Save the image
                              if (not new_image_path.exists()):
                                    # Save the image
                                    new_image.save(new_image_path)
                                    print(f"[INFO] Image saved. Path: {new_image_path}")
                              else:
                                    print(f"[WARNING] Unable to save new image because it already exists.")
                              ### End of Saving Procedure ###
                                    
                              # Store on database along with title, explanation e.t.c.
                              print(f"[INFO] Creating a new entry...")
                              # Create the new entry properties
                              new_entry_properties = [title, id, explanation, str(new_image_path), date]
                              try:
                                    # Check if entry exists
                                    exists = cursor.execute(f"SELECT title FROM entries WHERE title='{title}'")
                                    # Select from result set
                                    exists = cursor.fetchone()
                                    # Fetch current entry if exists
                                    #if (not os.path.exists(f"{new_image_path}")):
                                          # Execute the query
                                    cursor.execute(f"INSERT INTO entries(title, id, explanation, image_location, date) VALUES (?, ?, ?, ?, ?)", new_entry_properties)
                                    #else:
                                          # Warn user
                                    #      print("[INFO] Current entry already exists.")
                              except Exception as e:
                                    print(f"[ERROR] Unable to create entry: {e}")
                              
                              # Inform user about change commits
                              print("[INFO] Commiting changes...")
                              # Commit changes
                              database.commit()
                              # Inform user about the successfull operation
                              print(f"[INFO] Entry added successfully.")
                              
                        else:
                              print(f"[ERROR] Unable to fetch APOD image. Status code: {image_response.status_code}")
                  except Exception as e:
                        print(f"[ERROR] Unable to receive response: {e}")
            else:
                  print(f"[ERROR]: Unable to display APOD data: {apod_data}")
      except Exception as e:
            print(f"[ERROR] Unable to read NASA_API_KEY: {e}")
#
# Show the main menu
#
def main_interface():
      # Main interface
      print("""\n\n- Astronomy Picture of the Day Manager -\n
---------------- Welcome ---------------
-------------- Version 1.0 -------------\n
Type a function or 'HELP' for a list of available commands.\n""")
#
# Show the help menu
#
def help_interface():
      # Help interface
      print("""-      List of available commands      -\n
      UPDATE       # Update the database.
      VIEW         # View an entry based on it's ID.
      SEARCH       # Search for an entry to the database.
      SORT         # Sort the entries.
      LIST         # List all enties.
      APOD         # Display the current Astronomy Picture of the Day.
      HELP         # List all available commands.
      PING         # Ping the NASA server.
      API          # Modify the API key.
      CLEAR        # Clear the terminal.
      EXIT         # Exit the program.""")
#
# Auto update the database as a background process
#
def auto_update():
      # Inform user about the pending update
      print("[INFO] Updating database...")
      # Perform a database update
      update()
      # Inform user about the update completition
      print("[INFO] Update complete.")
      # The time sequence between updates
      time.sleep(3600)
#
# Establish connection with database
#
def connect(database_file):
      # Open the connection and return it to main
      #try:
            # Store the connection to a variable
            connection = sqlite3.connect(f"{database_file}.db")
            # Inform user about the successful connection
            print("[INFO] Connection with database established.")
            # Return connection to main
            return connection
      #except Exception as e:
            #print(f"[ERROR] Unable to establish connection with database: {e}")
            #return None
#
# Create a database cursor
#
""" def get_cursor(database):
      # Try to create a new cursor
      try:
            # Create the cursor
            cursor = database.cursor()
            # Inform the user about the successful creation of database cursor
            print("[INFO] Created cursor successfully.")
            # Return cursor to main
            return cursor
      except Exception as e:
            print(f"[ERROR] Unable to create database cursor: {e}")
            return None """
#
# Terminate the database connection
#
""" def terminate_connection(connection, cursor):
      # Terminate the connection with the database
      cursor.close()
      connection.close() """
#
# Main
#
if __name__ == "__main__":
      
      # Connect to database
      database = connect("database")
      # Create a cursor
      cursor = database.cursor()
      # Raise a system exit if can't connect to database
      #if (database_connection and cursor is None):
            # Warn user about errorous database connection.
      #      print("[ERROR] Database not responsive. Exiting...")
            # Raise the exit
      #      raise SystemExit
      #else:
            # Turn on auto_update process
            #update_process = multiprocessing.Process(target=auto_update)
            # Start the process
            #update_process.start()
      #     pass
      # Print the main interface
      main_interface()
      # The program loop
      while True:
            try:
                  # Change line
                  print("\n")
                  # User input handling
                  user_input = str(input()).lower()
                  
                  # Functions
                  if (user_input == "exit"):
                        # Exit the program
                        break
                  elif (user_input == "help"):
                        # Print the help interface
                        help_interface()
                  elif (user_input == "update"):
                        # Refresh database
                        update()
                  elif (user_input == "list"):
                        # Show all entries
                        list()
                  elif (user_input == "search"):
                        # Prompt a user input event
                        search_request = str(input(": "))
                        # Send request to search() function
                        search(search_request)
                  elif (user_input == "apod"):
                        # Print the image of day
                        apod()
                  elif (user_input == "delete"):
                        # Ask user which entry to remove by ID
                        delete_request = str(input(": "))
                        delete(delete_request)
                  elif (user_input == "view"):
                        # View a specific entry
                        view_request = str(input(": "))
                        view(view_request)
                  elif (user_input == "ping"):
                        # Ping the servers
                        ping(NASA_API_KEY)
                  elif (user_input == "api"):
                        # Change or modify API key
                        print("[INFO] Enter new API key.")
                        # Ask user for new API key
                        new_api = str(input(": "))
                        print("[INFO] Changing API key...")
                        # Try to verify the new API
                        response = ping(new_api)
                        # Check the response from the server
                        if (response == 200):
                              NASA_API_KEY = new_api
                              print("[INFO] API key changed successfully.")
                        else:
                              print("[ERROR] Unable to change API key.")
                  elif (user_input == "clear"):
                        # Clear the terminal
                        clear()
                  elif (user_input == ""):
                        # Just skip line
                        pass
                  else:
                        # Warn user for providing invalid input
                        print(f"[ERROR] Command '{user_input}'' not found.")
            # Handle keyboard interrupts
            except KeyboardInterrupt:
                  print("[WARNING] To exit the program type 'EXIT' on the prompt")
      #if (database and cursor is not None):
            # Close database connection
            #terminate_connection(database, cursor)
      print("[INFO] Closing cursor...")
      time.sleep(1)
      cursor.close()
      print("[INFO] Closed cursor.")
      time.sleep(1)
      print("[INFO] Closing database...")
      time.sleep(1)
      database.close()
      print("[INFO] Closed database.")
      # Warn user that auto_update process is about to stop
      print("[INFO] Terminating auto-update process...")
      # Terminate auto_update process when parent process terminated
      #update_process.terminate()
      # Wait a sec
      time.sleep(1)
      # Inform user
      print("[INFO] Terminating auto-update process... DONE")
      # Wait for another sec
      time.sleep(1)
#
# Program exit
#