
[{{ sender.profile.name}}]({{ sender.profile.get_absolute_url }}) wrote: 
**Congratulations!** You have won the **[{{ award.badge.name }}]({{ badge_url }})** <i class="{{ award.badge.icon }}"></i>
badge for the notable accomplishment of: *{{ award.badge.desc }}*.{% if post and post.root %}
You have earned this honor for: [{{ post.title}}]({{ post.get_absolute_url }})
{% endif %}
