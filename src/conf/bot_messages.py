START_MESSAGE = (
    "👋 Hello! I am your *GymFinder Bot* 🏋️‍♂️\n\n"
    "I can help you find gyms and fitness centers near you 🏃‍♀️💪\n\n"
    "📍 Please write the *city* and *country* where you want to find a gym.\n"
    "I will send you a CSV file 📑 with gyms in this area.\n\n"
    "📝 Format: `city, country`\n"
    "➡️ Example: `Sydney, Australia`"
)

FAIL_MESSAGE = (
    "❌ Sorry, I couldn't process your request.\n\n"
    "Please make sure you are using the correct format:\n"
    "📝 `city, country`\n\n"
    "➡️ Example: `Sydney, Australia`"
)

GYMS_LEN_MESSAGE = "I found {gyms_len} gyms in your area. \
                    You can download the CSV file with their details."