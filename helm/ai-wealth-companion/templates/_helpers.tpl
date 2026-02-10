{{/*
Expand the name of the chart.
*/}}
{{- define "ai-wealth-companion.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "ai-wealth-companion.fullname" -}}
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
{{- define "ai-wealth-companion.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ai-wealth-companion.labels" -}}
helm.sh/chart: {{ include "ai-wealth-companion.chart" . }}
{{ include "ai-wealth-companion.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: ai-wealth-companion
environment: {{ .Values.global.environment }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "ai-wealth-companion.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ai-wealth-companion.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Backend labels
*/}}
{{- define "ai-wealth-companion.backend.labels" -}}
{{ include "ai-wealth-companion.labels" . }}
app.kubernetes.io/component: api
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "ai-wealth-companion.backend.selectorLabels" -}}
{{ include "ai-wealth-companion.selectorLabels" . }}
app: {{ .Values.backend.name }}
app.kubernetes.io/component: api
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "ai-wealth-companion.frontend.labels" -}}
{{ include "ai-wealth-companion.labels" . }}
app.kubernetes.io/component: ui
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "ai-wealth-companion.frontend.selectorLabels" -}}
{{ include "ai-wealth-companion.selectorLabels" . }}
app: {{ .Values.frontend.name }}
app.kubernetes.io/component: ui
{{- end }}

{{/*
MCP Server labels
*/}}
{{- define "ai-wealth-companion.mcpServer.labels" -}}
{{ include "ai-wealth-companion.labels" . }}
app.kubernetes.io/component: mcp
{{- end }}

{{/*
MCP Server selector labels
*/}}
{{- define "ai-wealth-companion.mcpServer.selectorLabels" -}}
{{ include "ai-wealth-companion.selectorLabels" . }}
app: {{ .Values.mcpServer.name }}
app.kubernetes.io/component: mcp
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ai-wealth-companion.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ai-wealth-companion.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Namespace
*/}}
{{- define "ai-wealth-companion.namespace" -}}
{{- default .Release.Namespace .Values.global.namespace }}
{{- end }}
