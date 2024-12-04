from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
import os

class ActionSetUserInfo(Action):
    def name(self) -> Text:
        return "action_set_user_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Example user data; in practice, retrieve this from a database or API
        user_info = {
            "name": "Mohammad Norman",
            "gender": "Male",
            "age": 30,
            "balance": 1000.0
        }
        return [SlotSet("user", user_info)]



class ActionCheckSufficientFunds(Action):
    def name(self) -> Text:
        return "action_check_sufficient_funds"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        user_data = tracker.get_slot("user")
        if user_data:
            balance = user_data.get("balance", 0)
            transfer_amount = float(tracker.get_slot("amount"))
            has_sufficient_funds = transfer_amount <= balance
            return [SlotSet("has_sufficient_funds", has_sufficient_funds)]
        else:
            dispatcher.utter_message(text="User information is missing.")
            return []


class ActionGenerateReceipt(Action):
    def name(self) -> Text:
        return "action_generate_receipt"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Retrieve user data from the 'user' slot
        user_data = tracker.get_slot("user")
        if user_data:
            # Extract user information
            name = user_data.get("name")
            balance = user_data.get("balance", 0.0)

            # Retrieve transaction details
            recipient = tracker.get_slot("recipient")
            amount = float(tracker.get_slot("amount"))
            transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update user balance
            new_balance = balance - amount

            # Define the custom directory path for storing PDFs
            custom_directory = os.path.join(os.getcwd(), "receipts")
            os.makedirs(custom_directory, exist_ok=True)

            # Generate the filename for the receipt
            receipt_filename = f"receipt_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            receipt_filepath = os.path.join(custom_directory, receipt_filename)

            # Generate the receipt PDF
            pdf = SimpleDocTemplate(receipt_filepath, pagesize=letter)
            elements = []

            # Add a logo (replace 'logo.png' with your actual logo path)
            logo_path = os.path.join(os.getcwd(), "ewu.png")
            if os.path.exists(logo_path):
                elements.append(Image(logo_path, width=200, height=50))

            # Add receipt title
            elements.append(Table(
                [[f"Transaction Receipt"]],
                style=[
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkblue),
                    ('FONTSIZE', (0, 0), (-1, -1), 16),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]
            ))

            # Create a structured table for transaction details
            data = [
                ['Sender Name:', name],
                ['Recipient Name:', recipient],
                ['Transaction Date:', transaction_date],
                ['Amount Transferred:', f"{amount} BDT"],
                ['Remaining Balance:', f"{new_balance} BDT"],
            ]
            table = Table(data, colWidths=[150, 300])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(table)

            # Add a footer message
            elements.append(Table(
                [[f"Thank you for using our service."]],
                style=[
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkgreen),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 20),
                ]
            ))

            # Build the PDF
            pdf.build(elements)

            # Notify the user
            dispatcher.utter_message(text=f"The receipt has been generated and saved at: {receipt_filepath}")

            # Update the 'user' slot with the new balance
            user_data["balance"] = new_balance
            return [SlotSet("user", user_data)]
        else:
            dispatcher.utter_message(text="User information is missing.")
            return []

        
class ActionCheckBalance(Action):
    def name(self) -> Text:
        return "action_check_balance"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Retrieve user data from the 'user' slot
        user_data = tracker.get_slot("user")
        if user_data:
            # Extract the balance from user data
            balance = user_data.get("balance", 0.0)
            # Send the balance information to the user
            dispatcher.utter_message(text=f"Your current balance is {balance} BDT.")
        else:
            dispatcher.utter_message(text="User information is missing.")
        return []