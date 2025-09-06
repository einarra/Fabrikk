from fastapi import FastAPI
from supabase import create_client, Client
import os

# Initialize FastAPI
app = FastAPI()

# Initialize Supabase client
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.get("/quote/random")
async def get_random_quote():
    response = supabase.table("quotes").select("*").order("random()").limit(1).execute()
    quote = response.data[0] if response.data else {"message": "No quotes found."}
    return quote

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
