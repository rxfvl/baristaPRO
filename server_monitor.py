import os
import subprocess

SERVER_IP = "79.72.62.76"
SSH_KEY = "ssh-key-2026-04-27.key"
USER = "ubuntu"
PROJECT_DIR = "~/barista_backend"

def run_ssh(command, interactive=False):
    ssh_cmd = [
        "ssh", "-i", SSH_KEY, "-o", "StrictHostKeyChecking=no", f"{USER}@{SERVER_IP}",
        f"cd {PROJECT_DIR} && {command}"
    ]
    if interactive:
        subprocess.run(ssh_cmd)
    else:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True)
        return result.stdout, result.stderr

def print_menu():
    print("\n" + "="*50)
    print(" ☕ BaristaPRO - Server Monitor ☕ ")
    print("="*50)
    print("1. Ver estado de contenedores (ps)")
    print("2. Ver logs de la API (en vivo)")
    print("3. Ver logs de la Base de Datos (en vivo)")
    print("4. Reiniciar servidor completo (restart)")
    print("5. Apagar servidor (down)")
    print("6. Encender servidor (up -d)")
    print("7. Reconstruir API (up --build -d)")
    print("8. Salir")
    print("="*50)

def main():
    if not os.path.exists(SSH_KEY):
        print(f"Error: No se encuentra la llave SSH '{SSH_KEY}' en este directorio.")
        return

    while True:
        print_menu()
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            print("\n[INFO] Consultando estado de los contenedores...")
            run_ssh("sudo docker-compose ps", interactive=True)
        elif opcion == "2":
            print("\n[INFO] Cargando logs de la API... (Usa Ctrl+C para salir)")
            try:
                run_ssh("sudo docker logs -f --tail 100 barista_backend_api_1", interactive=True)
            except KeyboardInterrupt:
                pass
        elif opcion == "3":
            print("\n[INFO] Cargando logs de la DB... (Usa Ctrl+C para salir)")
            try:
                run_ssh("sudo docker logs -f --tail 100 barista_backend_db_1", interactive=True)
            except KeyboardInterrupt:
                pass
        elif opcion == "4":
            print("\n[INFO] Reiniciando contenedores...")
            run_ssh("sudo docker-compose restart", interactive=True)
        elif opcion == "5":
            print("\n[INFO] Apagando el servidor...")
            run_ssh("sudo docker-compose down", interactive=True)
        elif opcion == "6":
            print("\n[INFO] Encendiendo servidor...")
            run_ssh("sudo DOCKER_BUILDKIT=0 docker-compose up -d", interactive=True)
        elif opcion == "7":
            print("\n[INFO] Reconstruyendo y encendiendo la API...")
            run_ssh("sudo DOCKER_BUILDKIT=0 docker-compose up --build -d api", interactive=True)
        elif opcion == "8":
            print("Saliendo del monitor...")
            break
        else:
            print("[ERROR] Opción no válida. Inténtalo de nuevo.")

if __name__ == "__main__":
    # Evitar problemas de codificación de colores en Windows
    os.system('color')
    main()
