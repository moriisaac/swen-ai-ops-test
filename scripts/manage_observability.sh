#!/bin/bash
# SWEN AIOps Observability Stack Manager

echo "🔧 SWEN AIOps Observability Stack Manager"
echo "=========================================="

case "${1:-restart}" in
    "restart")
        echo "🔄 Restarting observability stack with clean configuration..."
        docker-compose down
        sleep 2
        docker-compose up -d
        echo "✅ Stack restarted with simplified Prometheus config!"
        echo ""
        echo "🌐 Access URLs:"
        echo "   • Prometheus: http://localhost:9090/targets"
        echo "   • Grafana:    http://localhost:3001 (admin/admin)"
        ;;
    "test")
        echo "🧪 Testing observability stack..."
        python test_grafana_setup.py
        ;;
    *)
        echo "Usage: $0 {restart|test}"
        echo "  restart - Restart with clean config"
        echo "  test    - Run test script"
        ;;
esac
