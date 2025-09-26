#!/bin/bash

# 相続税申告書類処理システム - バックエンド起動スクリプト

echo "🚀 相続税申告書類処理システム - Backend Starting..."

# Create necessary directories
mkdir -p uploads outputs logs temp

# Change to backend directory
cd backend

# Run the FastAPI server
python main.py