from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import aiohttp

# Leemos el token 
TOKEN = open("token", "r").read().strip()

# URL de la API
API_URL = "http://192.168.1.100/api"


# Funcion consultar_tienda()
# La utilizamos para consultar los datos de los sets en cualquier tienda
async def consultar_tienda(update: Update, context: ContextTypes.DEFAULT_TYPE, tienda: str):
    # Comprobamos que solo haya un parametro
    if len(context.args) != 1:
        await update.message.reply_text(
            f"Uso correcto:\n/{tienda} <número_de_set>\nEjemplo: /{tienda} 75400"
        )
        return
        
    # Construimos la URL del endpoint
    set_num = context.args[0]
    url = f"{API_URL}/{tienda}/{set_num}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                text = await response.text()
                print("STATUS:", response.status)
                print("RAW RESPONSE:", text)

                data = await response.json()

        # Si la API devuelve error, lo mostramos
        if "error" in data:
            await update.message.reply_text(f"Error: {data['error']}")
            return

        # Extraemos datos: el nombre de la tienda, el precio del set,
        # la disponibilidad y su URL
        site = data.get("site", tienda.capitalize())
        price = data.get("price", "Desconocido")
        status_raw = data.get("status", "Desconocido")
        url = data.get("url", "Desconocido")

        if status_raw == "Disponible":
            status = f"\U0001F7E2 {status_raw}"
        elif status_raw == "Agotado":
            status = f"\U0001F534 {status_raw}"
        else:
            status = status_raw


        # Mostramos la informacion
        msg = (
            f"Información del set *{set_num}:*\n"
            f"- Tienda: *{site}*\n"
            f"- Precio: *{price} €*\n"
            f"- Disponibilidad: *{status}*\n"
            f"- URL: {url}\n"
        )

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(
            f"Exception Error: {type(e).__name__}: {e}"
        )

# Definicion del comando /abacus
async def abacus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await consultar_tienda(update, context, "abacus")

# Definicion del comando /alcampo
async def alcampo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await consultar_tienda(update, context, "alcampo")

# Definicion del comando /brickboutique
async def brickoutique_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await consultar_tienda(update, context, "brickoutique")


# Definición del comando /bestprice
async def bestprice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Validación de parámetros
    if len(context.args) != 1:
        await update.message.reply_text(
            "Uso correcto:\n/bestprice <número_de_set>\nEjemplo: /bestprice 75345"
        )
        return

    set_num = context.args[0]

    # Validación básica
    if not set_num.isdigit():
        await update.message.reply_text("El número de set solo puede contener dígitos.")
        return

    # Construimos la URL del endpoint
    url = f"{API_URL}/bestprice/{set_num}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                raw = await response.text()
                print("STATUS:", response.status)
                print("RAW RESPONSE:", raw)

                data = await response.json()

        # Si la API devuelve un error, lo mostramos
        if "error" in data:
            await update.message.reply_text(f"Error: {data['error']}")
            return

        # No se ha encontrado en set en ninguna tienda
        if "warning" in data and "price" not in data:
            await update.message.reply_text(f"Atencion: {data['warning']}")
            return

        # Si no hay precio en los datos, mostramos un error
        if "price" not in data:
            await update.message.reply_text("Error: No se ha podido obtener informacion del set.")
            return

        # Obtenemos los datos
        site = data.get("site", "Desconocido")
        price = data.get("price", "Desconocido")
        status_raw = data.get("status", "Desconocido")
        url = data.get("url", "Desconocido")
        warning = data.get("warning", None)

        if status_raw == "Disponible":
            status = f"\U0001F7E2 {status_raw}"
        elif status_raw == "Agotado":
            status = f"\U0001F534 {status_raw}"
        else:
            status = status_raw
            
        # Construimos el mensaje
        msg = (
            f"Mejor precio para el set *{set_num}*:\n"
            f"- Tienda: *{site}*\n"
            f"- Precio: *{price} €*\n"
            f"- Estado: *{status}*\n"
            f"- URL: {url}\n"
        )

        if warning:
            msg += f"-Atencion: {warning}"

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(
            f"Exception Error: {type(e).__name__}: {e}"
        )


# Definicion del comando /setinfo
async def setinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Comprobamos que solo haya un parametro
    if len(context.args) != 1:
        await update.message.reply_text(
            "Uso correcto:\n/setinfo <número_de_set>\nEjemplo: /setinfo 75000"
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
        "/abacus - Muestra el precio de un set en Abacus\n"
        "/alcampo - Muestra el precio de un set en Alcampo\n"
        "/brickoutique - Muestra el precio de un set en Brickoutique\n"
        "/bestprice - Busca el mejor precio de un set en todas las tiendas\n"   
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
    app.add_handler(CommandHandler("abacus", abacus_command))
    app.add_handler(CommandHandler("alcampo", alcampo_command))
    app.add_handler(CommandHandler("brickoutique", brickoutique_command))
    app.add_handler(CommandHandler("bestprice", bestprice_command))

    # Iniciamos el bot en modo polling
    app.run_polling()

if __name__ == "__main__":
    main()
