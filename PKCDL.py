import requests
import os
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# Enter your API key below
api_key = "Enter your API key here"

class SetDownloader:
    def __init__(self):
        self.sets_data = None
        self.current_set = None
        self.card_data = None
        self.total_cards = 0
        self.cards_downloaded = 0
        
        # Create the GUI
        self.root = tk.Tk()
        self.root.title("Pokemon TCG Set Downloader")

        # Create the set selection dropdown
        self.set_label = ttk.Label(self.root, text="Select a set to download:")
        self.set_label.grid(column=0, row=0, padx=5, pady=5, sticky=tk.W)
        self.set_selection = ttk.Combobox(self.root, state="readonly")
        self.set_selection.grid(column=1, row=0, padx=5, pady=5, sticky=tk.W)
        
        # Create the progress bar
        self.progress_bar = ttk.Progressbar(self.root, mode="determinate")
        self.progress_bar.grid(column=0, row=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Create the download button
        self.download_button = ttk.Button(self.root, text="Download", command=self.download_set)
        self.download_button.grid(column=0, row=2, columnspan=2, padx=5, pady=5)

        # Create the folder selection button
        self.folder_button = ttk.Button(self.root, text="Select Download Folder", command=self.select_folder)
        self.folder_button.grid(column=0, row=3, columnspan=2, padx=5, pady=5)

        # Create a variable to store the selected download folder path
        self.download_folder_path = ""
        
        # Load the sets data from the API
        self.load_sets_data()
        
        # Start the GUI
        self.root.mainloop()
    
    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.download_folder_path = folder_path
    
    def load_sets_data(self):
        # Make a request to the Pokemon TCG API to get a list of all sets
        sets_response = requests.get(f"https://api.pokemontcg.io/v2/sets", headers={"X-Api-Key": api_key})
        self.sets_data = sets_response.json()["data"]
        
        # Populate the set selection dropdown
        self.set_selection["values"] = [set_data["name"] for set_data in self.sets_data]
    
    def download_set(self):
        # Get the currently selected set
        self.current_set = self.set_selection.get()
        
        # Make a request to the Pokemon TCG API to get a list of all cards for this set
        set_id = next(set_data["id"] for set_data in self.sets_data if set_data["name"] == self.current_set)
        cards_response = requests.get(f"https://api.pokemontcg.io/v2/cards?q=set.id:{set_id}", headers={"X-Api-Key": api_key})
        self.card_data = cards_response.json()["data"]
        
        # Set the progress bar maximum value
        self.total_cards = len(self.card_data)
        self.progress_bar["maximum"] = self.total_cards
        
        # Create a directory for this set
        set_folder_path = os.path.join(self.download_folder_path, self.current_set)
        os.makedirs(set_folder_path, exist_ok=True)
        
        # Download each card image in a separate thread
        for card_index, card_data in enumerate(self.card_data):
            card_thread = threading.Thread(target=self.download_card_image, args=(card_index, card_data, set_folder_path))
            card_thread.start()

    def download_card_image(self, card_index, card_data, set_folder_path):
        card_id = card_data["id"]
        card_number = card_data["number"]
        card_name = card_data["name"]
        card_image_url = card_data["images"]["large"]
        
        # Download the card image
        card_image_response = requests.get(card_image_url)
        
        # Save the card image to a file in the set folder
        with open(os.path.join(set_folder_path, f"{card_number} {card_name}.png"), "wb") as card_image_file:
            card_image_file.write(card_image_response.content)
        
        # Update the progress bar
        self.cards_downloaded += 1
        self.progress_bar["value"] = self.cards_downloaded
        
        # Update the GUI with the current progress
        self.root.update_idletasks()


if __name__ == '__main__':
    set_downloader = SetDownloader()
