{{/*
Expand the name of the chart.
*/}}
{{- define "notifyhub-lite.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "notifyhub-lite.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "notifyhub-lite.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "notifyhub-lite.labels" -}}
helm.sh/chart: {{ include "notifyhub-lite.chart" . }}
{{ include "notifyhub-lite.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "notifyhub-lite.selectorLabels" -}}
app.kubernetes.io/name: {{ include "notifyhub-lite.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "notifyhub-lite.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "notifyhub-lite.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the PostgreSQL connection URL
*/}}
{{- define "notifyhub-lite.databaseUrl" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "postgresql://%s:%s@%s-postgresql:5432/%s" .Values.postgresql.auth.username .Values.postgresql.auth.password .Release.Name .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.config.databaseUrl | default "postgresql://notifyhub:secure-password-123@localhost:5432/notifyhublite" }}
{{- end }}
{{- end }}

{{/*
Create SMTP host
*/}}
{{- define "notifyhub-lite.smtpHost" -}}
{{- if .Values.postfix.enabled }}
{{- printf "%s-postfix" (include "notifyhub-lite.fullname" .) }}
{{- else }}
{{- .Values.smtp.host }}
{{- end }}
{{- end }}
