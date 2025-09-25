# NotifyHubLite Kubernetes Deployment

## 🎉 Deployment Status: SUCCESS

NotifyHubLite has been successfully deployed to Kubernetes using Helm!

## 📊 Deployment Overview

### Components Deployed
- **NotifyHubLite API**: 2 replicas running
- **Postfix SMTP Server**: 1 replica running
- **Services**: ClusterIP services for internal communication
- **Secrets**: GHCR authentication configured
- **ConfigMaps**: Application configuration

### Container Images
- **API Application**: `ghcr.io/johnnynv/notifyhub-lite:1.0.0`
- **SMTP Server**: `juanluisbaptiste/postfix:latest`

## 🔧 Helm Chart Structure

```
helm/notifyhub-lite/
├── Chart.yaml                    # Chart metadata
├── values.yaml                   # Default configuration
└── templates/
    ├── _helpers.tpl              # Template helpers
    ├── configmap.yaml            # Configuration
    ├── secret.yaml               # Sensitive data
    ├── serviceaccount.yaml       # Service account
    ├── deployment.yaml           # Main application
    ├── service.yaml              # Service definition
    ├── ingress.yaml              # Ingress (optional)
    ├── hpa.yaml                  # Auto-scaling (optional)
    ├── postfix-deployment.yaml   # SMTP server
    └── postfix-service.yaml      # SMTP service
```

## 🚀 Deployment Commands

### Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace notifyhub-lite

# Create GHCR secret for private registry
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<your name> \
  --docker-password=<your password> \
  --docker-email=johnnynv@nvidia.com \
  --namespace=notifyhub-lite

# Install with Helm
helm install notifyhub-lite helm/notifyhub-lite \
  --namespace notifyhub-lite \
  --set postgresql.enabled=false \
  --set config.serverIp="10.78.14.61" \
  --set config.apiKey="notify-hub-k8s-api-key-123" \
  --set "imagePullSecrets[0].name=ghcr-secret"
```

### Check Deployment Status
```bash
# View all resources
kubectl get all -n notifyhub-lite

# Check logs
kubectl logs -n notifyhub-lite deployment/notifyhub-lite
kubectl logs -n notifyhub-lite deployment/notifyhub-lite-postfix
```

## 🧪 Testing the Deployment

### Health Check
```bash
# Test internally within cluster
kubectl run test-client --rm -i --image=curlimages/curl --restart=Never -n notifyhub-lite -- \
  curl -s http://notifyhub-lite/health
```

### Send Test Email
```bash
kubectl run test-email --rm -i --image=curlimages/curl --restart=Never -n notifyhub-lite -- \
  curl -X POST "http://notifyhub-lite/api/v1/emails/send-plain" \
  -H "Authorization: Bearer notify-hub-k8s-api-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["test@example.com"],
    "subject": "Test from K8s",
    "body": "Hello from NotifyHubLite in Kubernetes!"
  }'
```

## 📋 Current Configuration

| Component | Status | Replicas | Image |
|-----------|--------|----------|-------|
| API Server | ✅ Running | 2/2 | ghcr.io/johnnynv/notifyhub-lite:1.0.0 |
| SMTP Server | ✅ Running | 1/1 | juanluisbaptiste/postfix:latest |

### Services
- **notifyhub-lite**: ClusterIP `10.96.112.247:80`
- **notifyhub-lite-postfix**: ClusterIP `10.108.1.191:25`

### Configuration
- **Server IP**: 10.78.14.61
- **Domain**: 10.78.14.61.nip.io
- **API Key**: notify-hub-k8s-api-key-123
- **SMTP Relay**: smtp.nvidia.com:25

## 🔄 Management Commands

### Update Deployment
```bash
# Upgrade with new values
helm upgrade notifyhub-lite helm/notifyhub-lite \
  --namespace notifyhub-lite \
  --set config.apiKey="new-api-key"

# Rollback if needed
helm rollback notifyhub-lite 1 -n notifyhub-lite
```

### Scale Application
```bash
# Scale API pods
kubectl scale deployment notifyhub-lite --replicas=3 -n notifyhub-lite
```

### Cleanup
```bash
# Uninstall
helm uninstall notifyhub-lite -n notifyhub-lite

# Delete namespace
kubectl delete namespace notifyhub-lite
```

## ✅ Test Results

**API Health Check**: ✅ SUCCESS
```json
{"status":"healthy","service":"NotifyHubLite API","version":"1.0.0"}
```

**Email Sending**: ✅ SUCCESS  
```json
{"email_id":"bd175822-33e8-48bd-be85-bb9fdafd48c7","status":"success","message":"Plain text email sent successfully."}
```

## 🎯 Next Steps

1. **Enable Ingress** for external access
2. **Add TLS/SSL** certificates
3. **Configure monitoring** and alerting
4. **Set up persistent storage** if needed
5. **Enable autoscaling** based on load

The NotifyHubLite email notification system is now successfully running in your Kubernetes cluster! 🚀
