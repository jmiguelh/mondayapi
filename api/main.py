import os
import requests
import json
from dotenv import load_dotenv
from monday import MondayClient

load_dotenv()

apiKey = os.getenv("API_KEY")
apiUrl = os.getenv("BASE_URL")
headers = {"Authorization": apiKey}
board = 5808464075

query = """
 {
  boards(ids: 5808464075) {
    groups {
      id
      title
      position
      color
      items_page(limit: 100) {
        items {
          id
          name
          column_values {
            column {
              title
            }
            text
          }
        }
      }
    }
  }
}
"""
data = {"query": query}

r = requests.post(url=apiUrl, json=data, headers=headers)  # make request
print(r.json())


# monday = MondayClient(apiKey)

# monday.boards.fetch_boards_by_id(5808464075)
# monday.boards.fetch_items_by_board_id(board_ids=5808464075, limit=50)
