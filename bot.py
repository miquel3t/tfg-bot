from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import aiohttp

# Leemos el token 
TOKEN = open("token", "r").read().strip()

# URL de la API
API_URL = "http://192.168.1.100/api"

# Definicion del comando /setinfo
async def setinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Comprovamos que solo haya un parametro
    if len(context.args) != 1:
        await update.message.reply_text(
            "Uso correcto:\n/setinfo <número_de_set>\nEjemplo: /setinfo 75000-1"
        )
        return

    # Construimos la URL del endpoint
    set_num = context.args[0]
    url = f"{API_URL}/setinfo/{set_num}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                text = await response.text()
                print("STATUS:", response.status)
                print("TEXT:", text)

                data = await response.json()
 
        # Si la API devuelve un error, lo mostramos
        if "error" in data:
            await update.message.reply_text(f"Error: {data['error']}")
            return

        # Obtenemos el nombre del set, el tema, el año, su imagen, y la informacion
        # de las minifiguras
        name = data.get("name", "Desconocido")
        year = data.get("year", "Desconocido")
        theme = data.get("theme_name", "Desconocido")
        img = data.get("set_img_url", "")
        minifigs = data.get("minifigs", [])

        # Mostramos la informacion
        msg = (
            f"Información del set *{set_num}*:\n"
            f"- Nombre: *{name}*\n"
            f"- Año: *{year}*\n"
            f"- Tema: *{theme}*\n"
        )

        if img:
            msg += f"- Imagen: {img}\n"

        if minifigs:
            msg += "\n*Minifiguras incluidas:*\n"
            for fig in minifigs:
                msg += (
                    f"• *{fig.get('name', '???')}* "
                    f"(x{fig.get('quantity', 1)})\n"
                    f"  {fig.get('fig_img_url', '')}\n"
                )
        else:
            msg += "\n(No contiene minifiguras)\n"

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(
            f"Exception Error: {type(e).__name__}: {e}"
        )



# Definicion del comando /health
async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Construimos la URL del endpoint
    url = f"{API_URL}/health"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=3) as response:
                text = await response.text()
                print("STATUS:", response.status)
                print("TEXT:", text)

                data = await response.json()

        status = data.get("status", "unknown")
        database = data.get("database", "unknown")

        msg = (
            f"Estado de la API:\n"
            f"- API: `{status}`\n"
            f"- Base de datos: `{database}`"
        )

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception:    
        await update.message.reply_text(
            "Exception Error: no puedo contactar con la API."
        )

# Definicion del comando /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Respuesta al comando /start
    await update.message.reply_text(
        "¡Bienvenido!\n"
        "Usa /help para ver lo que puedo hacer."
    )

# Definicion del comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Respuesta al comando help
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start – Inicia la conversación\n"
        "/help – Muestra esta ayuda\n"
        "/health - Comprueba el estado de la API\n"
        "/setinfo - Muestra informacion de un set\n"
        "¡Esto es todo! Por el momento..."
    )

def main():
    # Iniciamos el bot
    app = ApplicationBuilder().token(TOKEN).build()

    # Registramos los comandos
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("health", health_command))
    app.add_handler(CommandHandler("setinfo", setinfo_command))

    # Iniciamos el bot en modo polling
    app.run_polling()

if __name__ == "__main__":
    main()
