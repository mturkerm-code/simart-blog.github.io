---
layout: default
title: "Enerji Verimliliği"
meta_description: "Akıllı ev enerji yönetimi, elektrik tasarrufu, verimli cihazlar ve sürdürülebilir teknoloji çözümleri"
---

# Enerji Verimliliği

Akıllı ev enerji yönetimi, elektrik tasarrufu ve verimli cihazlar hakkında yazılar.

{% assign posts = site.categories["enerji-verimliligi"] %}
{% if posts %}
{% for post in posts %}
- [{{ post.title }}]({{ post.url | relative_url }}) - {{ post.date | date: "%d %B %Y" }}
{% endfor %}
{% else %}
Henüz yazı bulunmuyor.
{% endif %}

---

*Şımart Teknoloji - Akıllı ev enerji çözümleri*