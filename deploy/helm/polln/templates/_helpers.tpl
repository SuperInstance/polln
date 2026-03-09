{{- /*
Copyright 2024 POLLN Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/}}

{{/* vim: set filetype=mustache: */}}

{{/*
Expand the name of the chart.
*/}}
{{- define "polln.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "polln.fullname" -}}
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
{{- define "polln.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "polln.labels" -}}
helm.sh/chart: {{ include "polln.chart" . }}
{{ include "polln.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "polln.selectorLabels" -}}
app.kubernetes.io/name: {{ include "polln.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "polln.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "polln.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Redis connection URL
*/}}
{{- define "polln.redisUrl" -}}
{{- if .Values.redis.enabled }}
{{- printf "redis://%s:%s" (include "polln.redisHost" .) (include "polln.redisPort" .) }}
{{- else }}
{{- printf "redis://%s:%s" .Values.polln.env.REDIS_HOST .Values.polln.env.REDIS_PORT }}
{{- end }}
{{- end }}

{{/*
Redis host
*/}}
{{- define "polln.redisHost" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" .Release.Name }}
{{- else }}
{{- .Values.polln.env.REDIS_HOST }}
{{- end }}
{{- end }}

{{/*
Redis port
*/}}
{{- define "polln.redisPort" -}}
{{- if .Values.redis.enabled }}
{{- "6379" }}
{{- else }}
{{- .Values.polln.env.REDIS_PORT | default "6379" }}
{{- end }}
{{- end }}

{{/*
PostgreSQL host
*/}}
{{- define "polln.postgresqlHost" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" .Release.Name }}
{{- else }}
{{- .Values.polln.env.DB_HOST }}
{{- end }}
{{- end }}

{{/*
PostgreSQL port
*/}}
{{- define "polln.postgresqlPort" -}}
{{- if .Values.postgresql.enabled }}
{{- "5432" }}
{{- else }}
{{- .Values.polln.env.DB_PORT | default "5432" }}
{{- end }}
{{- end }}

{{/*
Anti-affinity rules
*/}}
{{- define "polln.antiAffinity" -}}
{{- if eq .Values.antiAffinity.type "hard" }}
podAntiAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
  - labelSelector:
      matchExpressions:
      - key: app.kubernetes.io/name
        operator: In
        values:
        - {{ include "polln.name" . }}
      - key: app.kubernetes.io/instance
        operator: In
        values:
        - {{ .Release.Name }}
    topologyKey: {{ .Values.antiAffinity.topologyKey }}
{{- else }}
podAntiAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100
    podAffinityTerm:
      labelSelector:
        matchExpressions:
        - key: app.kubernetes.io/name
          operator: In
          values:
          - {{ include "polln.name" . }}
        - key: app.kubernetes.io/instance
          operator: In
          values:
          - {{ .Release.Name }}
      topologyKey: {{ .Values.antiAffinity.topologyKey }}
{{- end }}
{{- end }}
