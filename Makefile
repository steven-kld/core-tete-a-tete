.PHONY: clean prod down up logs restart

# Remove containers, volumes, networks
clean:
	@echo "🧹 Cleaning Docker containers and volumes..."
	docker compose down --volumes --remove-orphans
	docker system prune -f

# Full rebuild and production start
prod: clean
	@echo "🚀 Building and starting production..."
	docker compose -f compose.yaml up --build -d

# Stop containers
down:
	@echo "🛑 Stopping containers..."
	docker compose down

# Start without cleaning
up:
	@echo "⬆️  Starting containers..."
	docker compose -f compose.yaml up --build -d

# View logs
logs:
	@echo "📜 Tailing logs (Ctrl+C to stop)..."
	docker compose logs -f

# Restart services (without rebuilding)
restart:
	@echo "🔄 Restarting services..."
	docker compose restart
