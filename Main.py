import pandas as pd
import numpy as np
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ticket = pd.read_csv("Data/tickets.csv")
agents = pd.read_csv("Data/agents.csv")

ticket.reset_index(drop=True, inplace=True)
agents.reset_index(drop=True, inplace=True)

# print(ticket.columns)
# print(ticket.shape)
# print(ticket.head())

ticket = ticket.sort_values("source_system")
ticket.drop_duplicates("ticket_id",inplace=True)

ticket["created_at"].dtype
ticket["created_at"] = pd.to_datetime(ticket["created_at"])
ticket["weeks"] = ticket["created_at"].dt.to_period("W").astype(str)

# ticket["category"].value_counts()

def run_analysis():

    ticket["corrected_categories"] = ticket["category"]

    categories = [
    category for category in ticket["category"].unique()
    if category != "Other"
]

    # categories = ticket["category"].unique()

    if os.path.exists("labels.csv"):
        labels = pd.read_csv("labels.csv")
    else:
        labels = pd.DataFrame(
            columns=["ticket_id", "predicted_category"]
        )

    # classified_tickets = set(labels["ticket_id"])
    # other_tickets = ticket[(ticket["category"] == "Other") & (~ticket["ticket_id"].isin(classified_tickets))].head(250).index

    
    # other_tickets = ticket[
    # ticket["category"] == "Other"
    # ].head(44).index


    other_tickets = []

    for i in other_tickets:

        message = ticket.loc[i , "customer_message"]

        prompt = f""" Classify this customer support message into exactly ONE category.

        Allowed categories:
        {categories}

        Customer message:
        {message}

        Rules:
        - Use only the allowed categories.
        - Do not create a new category.
        - Return only the category name.
        """


        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = response.choices[0].message.content.strip()
        ticket.loc[i , "corrected_categories"] = result

        labels.loc[len(labels)] = ticket.loc[i , "ticket_id"] , result 

        labels.to_csv("labels.csv", index=False)

    for i in labels.index:
        ticket.loc[
            ticket["ticket_id"] == labels.loc[i, "ticket_id"],
            "corrected_categories"
        ] = labels.loc[i, "predicted_category"]    

    agents_f = agents[agents["team"] != "Escalations & Warranty"]

    weekly_digest = (
        ticket.groupby(["weeks", "corrected_categories"])
              .size()
              .reset_index(name="ticket_count")
    )

    weekly_agents = (
        ticket[ticket["status"].isin(["resolved", "closed"]) & ticket["agent_id"].isin(agents_f["agent_id"])]
        .groupby(["weeks", "agent_id"])
        .size()
        .reset_index(name="tickets_closed")
    ) 

    # agents["team"].unique()
    # agents["agent_id"].duplicated().sum()

    
    agent_info = agents_f[["agent_id", "name"]]

    weekly_agents = weekly_agents.merge(
        agent_info,
        on="agent_id",
        how="left"
    )

    weekly_agents = weekly_agents.sort_values(
        ["weeks", "tickets_closed"],
        ascending=[True, False]
    )

    return ticket, weekly_digest, weekly_agents


def calculate_business_outcome(ticket):

    ticket_sorted = ticket.sort_values(
        ["customer_id", "created_at"]
    )

    ticket_sorted["days"] = (
        ticket_sorted
        .groupby("customer_id")["created_at"]
        .diff()
        .dt.days
    )

    repeat_contacts = ticket_sorted[
        ticket_sorted["days"].between(0, 7)
    ]

    

    total_contacts = len(ticket)
    repeat_count = len(repeat_contacts)
    repeat_rate = repeat_count / total_contacts * 100
    repeat_cost = repeat_count * 290

    return total_contacts, repeat_count, repeat_rate, repeat_cost

if __name__ == "__main__":
    ticket, weekly_digest, weekly_agents = run_analysis()