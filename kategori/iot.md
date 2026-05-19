---
layout: default
title: "IoT ve Sensör Teknolojileri"
meta_description: "IoT cihazları, sensör teknolojileri, nesnelerin interneti ve akıllı cihaz entegrasyonu hakkında güncel bilgiler"
---

# IoT ve Sensör Teknolojileri

Nesnelerin interneti, sensör teknolojileri ve IoT cihaz entegrasyonu hakkında yazılar.

{% assign posts = site.categories["iot"] %}
{% if posts %}
{% for post in posts %}
- [{{ post.title }}]({{ post.url | relative_url }}) - {{ post.date | date: "%d %B %Y" }}
{% endfor %}
{% else %}
Henüz yazı bulunmuyor.
{% endif %}

---

*Şımart Teknoloji - Türkiye'nin yerli IoT teknolojileri üreticisi*