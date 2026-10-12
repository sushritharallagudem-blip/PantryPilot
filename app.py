
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
from datetime import date
import json
import os
import requests
from dotenv import load_dotenv
from memory import remember, recall
from fastapi import Request

app = FastAPI(title="PantryPilot")
load_dotenv(Path(__file__).parent / ".env", override=True)

LYZR_API_KEY = os.getenv("LYZR_API_KEY")
LYZR_AGENT_ID = os.getenv("LYZR_AGENT_ID")

LYZR_API_URL = "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"

DATA_FILE = Path(__file__).parent / "pantry.json"


def load_pantry():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except json.JSONDecodeError:
            return []
    return []


def save_pantry(items):
    DATA_FILE.write_text(json.dumps(items, indent=2))


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PantryPilot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f3f7ef;
            color: #263b2b;
            max-width: 800px;
            margin: 35px auto;
            padding: 20px;
        }
        h1 { color: #326b45; }
        .card {
            background: white;
            padding: 22px;
            border-radius: 16px;
            margin: 20px 0;
            box-shadow: 0 3px 12px #0001;
        }
        input, button {
            padding: 12px;
            margin: 6px 3px 6px 0;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 15px;
        }
        button {
            background: #326b45;
            color: white;
            border: none;
            cursor: pointer;
        }
        li { padding: 10px 0; }
        .warning { color: #b45309; font-weight: bold; }
        .safe { color: #326b45; }
        .remove { background: #a33; padding: 7px; }
    </style>
</head>
<body>
    <h1>🌿 PantryPilot</h1>
    <p>Your smart kitchen assistant — waste less, eat better.</p>

    <div class="card">
        <h2>🥬 My Pantry</h2>
        <p>Add ingredients and their expiry dates.</p>
        <form id="foodForm">
            <input id="food" placeholder="Ingredient name" required>
            <input id="expiry" type="date" required>
            <button type="submit">Add to pantry</button>
        </form>
        <p id="message"></p>
        <ul id="items"></ul>
    </div>

    <div class="card">
        <h2>⏰ Expiry Alerts</h2>
        <p id="summary">Checking your pantry...</p>
    </div>

<div class="card">
    <h2>🍳 Meal Suggestions</h2>
    <p>Find meals using ingredients in your pantry.</p>
    <button onclick="suggestMeals()">Suggest a meal</button>
    <button onclick="askPantryAI()">Ask PantryPilot AI</button>
    <div id="mealResults"></div>
</div>



<script>
async function loadItems() {
    const response = await fetch('/api/pantry');
    const items = await response.json();
    const list = document.getElementById('items');
    list.replaceChildren();

    let urgent = 0;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    items.forEach(item => {
        const expiryDate = new Date(item.expiry + 'T00:00:00');
        const days = Math.round((expiryDate - today) / 86400000);

        const li = document.createElement('li');
        const details = document.createElement('span');

        let status = '';
        if (days < 0) {
            status = ' ⚠️ Expired';
            li.className = 'warning';
            urgent++;
        } else if (days === 0) {
            status = ' ⚠️ Expires today';
            li.className = 'warning';
            urgent++;
        } else if (days <= 3) {
            status = ' ⚠️ Use soon — ' + days + ' day(s) left';
            li.className = 'warning';
            urgent++;
        } else {
            status = ' ✓ ' + days + ' day(s) left';
            li.className = 'safe';
        }

        details.textContent =
            item.name + ' — ' + item.expiry + status + ' ';

        const remove = document.createElement('button');
        remove.textContent = 'Remove';
        remove.className = 'remove';
        remove.onclick = async () => {
            await fetch('/api/pantry/' + item.id, {method: 'DELETE'});
            await loadItems();
        };

        li.append(details, remove);
        list.appendChild(li);
    });

    document.getElementById('summary').textContent =
    items.length === 0
    ? 'Your pantry is empty. Add an ingredient to get started!'
    : urgent + ' ingredient(s) need attention out of ' +
      items.length + ' total. Check the pantry list above for expiry dates.';
}

document.getElementById('foodForm').addEventListener('submit',
async event => {
    event.preventDefault();

    const name = document.getElementById('food').value.trim();
    const expiry = document.getElementById('expiry').value;

    const response = await fetch('/api/pantry', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, expiry})
    });

    if (response.ok) {
        document.getElementById('message').textContent =
            'Ingredient saved successfully!';
        document.getElementById('food').value = '';
        document.getElementById('expiry').value = '';
        await loadItems();
    } else {
        document.getElementById('message').textContent =
            'Please enter a valid ingredient and expiry date.';
    }
});

async function suggestMeals() {
    const response = await fetch('/api/pantry');
    const items = await response.json();

    const ingredients = items.map(item =>
        item.name.toLowerCase()
    );

    const recipes = [
        {
            name: "Spinach Omelette",
            ingredients: ["spinach", "egg", "eggs"],
            description: "A quick protein-rich breakfast."
        },
        {
            name: "Tomato Spinach Curry",
            ingredients: ["tomato", "tomatoes", "spinach"],
            description: "A simple vegetable curry."
        },
        {
            name: "Vegetable Stir-Fry",
            ingredients: ["carrot", "capsicum", "broccoli"],
            description: "A colourful, quick meal."
        },
        {
            name: "Tomato Egg Scramble",
            ingredients: ["tomato", "tomatoes", "egg", "eggs"],
            description: "An easy meal with protein."
        }
    ];

    const matches = recipes.map(recipe => ({
        ...recipe,
        matched: recipe.ingredients.filter(ingredient =>
            ingredients.some(item => item.includes(ingredient))
        )
    })).filter(recipe => recipe.matched.length > 0)
      .sort((a, b) => b.matched.length - a.matched.length);

    const results = document.getElementById('mealResults');
    results.replaceChildren();

    if (matches.length === 0) {
        results.textContent =
            "Add ingredients such as spinach, tomatoes, or eggs to get suggestions.";
        return;
    }

    matches.forEach(recipe => {
        const card = document.createElement('div');
        const title = document.createElement('h3');
        const description = document.createElement('p');
        const matched = document.createElement('p');

        title.textContent = "🍽️ " + recipe.name;
        description.textContent = recipe.description;
        matched.textContent =
            "Pantry ingredients matched: " + recipe.matched.join(", ");

        card.append(title, description, matched);
        results.appendChild(card);
    });
}


async function askPantryAI() {
    const results = document.getElementById("mealResults");
    results.textContent = "PantryPilot AI is thinking...";

    try {
        const response = await fetch("/api/ai-meal-suggestion", {
            method: "POST"
        });

        const data = await response.json();

        if (data.suggestion) {
            
results.innerHTML = data.suggestion
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/^### (.*)$/gm, "<h4>$1</h4>")
    .replace(/^## (.*)$/gm, "<h3>$1</h3>")
   .replace(/\\n/g, "<br>");

        } else {
            results.textContent = data.error || "Could not get an AI suggestion.";
        }
    } catch (error) {
        results.textContent = "Could not connect to PantryPilot AI. Please try again.";
    }
}


loadItems();
</script>
</body>
</html>
"""


@app.get("/api/pantry")
def get_pantry():
    return load_pantry()


@app.post("/api/pantry")
def add_ingredient(item: dict):
    name = str(item.get("name", "")).strip()
    expiry = str(item.get("expiry", ""))

    if not name or len(name) > 100:
        return {"error": "Enter a valid ingredient name"}

    try:
        date.fromisoformat(expiry)
    except ValueError:
        return {"error": "Enter a valid expiry date"}

    items = load_pantry()
    new_item = {
        "id": max((x.get("id", 0) for x in items), default=0) + 1,
        "name": name,
        "expiry": expiry
    }
    items.append(new_item)
    save_pantry(items)
    return new_item


@app.delete("/api/pantry/{item_id}")
def delete_ingredient(item_id: int):
    items = load_pantry()
    updated = [x for x in items if x.get("id") != item_id]

    if len(updated) == len(items):
        return {"error": "Ingredient not found"}

    save_pantry(updated)
    return {"message": "Ingredient removed"}

@app.post("/api/ai-meal-suggestion")
def ai_meal_suggestion():
    if not LYZR_API_KEY or not LYZR_AGENT_ID:
        return {"error": "Lyzr API key or Agent ID is missing. Check your .env file."}

    pantry = load_pantry()

    if not pantry:
        return {"error": "Your pantry is empty. Add some ingredients first."}

    pantry_details = []

    for item in pantry:
        name = item.get("name", "Unknown ingredient")
        expiry = item.get("expiry", "Expiry date not provided")
        pantry_details.append(f"- {name}: expires {expiry}")

  
        
    # Save current pantry items as memories.
    for item in pantry:
        remember(
            f"{item.get('name', 'Unknown ingredient')} expires {item.get('expiry', 'date unknown')}",
            "pantry"
        )

    # Retrieve relevant saved memories.
    memories = recall(
        "Which ingredients expire soon and what meal decisions are relevant?",
        limit=5
    )

    memory_context = "\n".join(f"- {item}" for item in memories)

   
        
    previous_recipes = recall(
        "What meals or recipes have already been suggested?",
        limit=10
    )

    previous_recipe_context = "\n".join(
        f"- {item}" for item in previous_recipes
    )

    message = (
        "You are PantryPilot, a creative kitchen assistant.\n"
        "Suggest ONE practical recipe using the current pantry.\n"
        "IMPORTANT: Choose a meaningfully different recipe from previous suggestions. "
        "Do not repeat the same dish or merely rename it.\n"
        "Vary the cooking method and recipe style when possible.\n"
        "Prioritize ingredients that expire soon.\n"
        "Do not invent available ingredients or expiry dates.\n"
        "List the recipe name, ingredients, and numbered cooking steps.\n\n"
        "CURRENT PANTRY:\n" + "\n".join(pantry_details) +
        "\n\nRELEVANT PANTRY MEMORIES:\n" + memory_context +
        "\n\nPREVIOUS RECIPE SUGGESTIONS TO AVOID:\n" +
        (previous_recipe_context or "No previous recipes recorded.")
    )

    

    

    payload = {
        "user_id": "pantrypilot-user",
        "agent_id": LYZR_AGENT_ID,
        "session_id": "pantrypilot-session",
        "message": message
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": LYZR_API_KEY
    }

    try:
        response = requests.post(
            LYZR_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        ai_answer = result.get("response")

        if not ai_answer:
            ai_answer = result.get("message")

        if not ai_answer:
            return {"error": "Lyzr responded, but the answer format was unexpected."}

        remember(f"Previously suggested recipe: {ai_answer}", "recipe_history")

        return {"suggestion": ai_answer}


    except requests.exceptions.Timeout:
        return {"error": "Lyzr took too long to respond. Please try again."}

    except requests.exceptions.HTTPError as exc:
        print("Lyzr HTTP error:", exc.response.status_code, exc.response.text[:500])
        return {"error": "Lyzr rejected the request. Check your API configuration and endpoint."}

    except requests.exceptions.RequestException as exc:
        print("Lyzr connection error:", str(exc))
        return {"error": "Could not connect to Lyzr. Please try again."}

    except (ValueError, AttributeError):
        return {"error": "Lyzr returned an unexpected response."}


@app.post("/api/omi-transcript")
async def omi_transcript(request: Request):
    try:
        segments = await request.json()

        if not isinstance(segments, list):
            return {"error": "Expected a list of transcript segments."}

        saved = 0

        for segment in segments:
            if not isinstance(segment, dict):
                continue

            text = str(segment.get("text", "")).strip()
            if not text:
                continue

            # Store the transcript in Qdrant for semantic retrieval.
            remember(text, "omi_transcript")
            saved += 1

        return {
            "status": "success",
            "segments_received": len(segments),
            "segments_saved": saved
        }

    except Exception as exc:
        print("Omi transcript error:", str(exc))
        return {"error": "Could not process the Omi transcript."}

@app.get("/api/memory-check")
def memory_check():
    try:
        memories = recall(
            "pantry ingredients and expiry dates",
            limit=5
        )
        return {
            "memory_count": len(memories),
            "memories": memories
        }
    except Exception as exc:
        print("Memory check error:", str(exc))
        return {"error": "Could not retrieve pantry memories."}


