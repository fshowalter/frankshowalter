!function(e){function t(e){var t,n=new Date(e),a=n.getTime(),r=[[60,"seconds",1],[120,"1 minute ago","1 minute from now"],[3600,"minutes",60],[7200,"1 hour ago","1 hour from now"],[86400,"hours",3600],[172800,"Yesterday","Tomorrow"],[604800,"days",86400],[1209600,"Last week","Next week"],[2419200,"weeks",604800],[4838400,"Last month","Next month"],[29030400,"months",2419200],[58060800,"Last year","Next year"],[290304e4,"years",29030400]],o=0,s=r[o],i=(+new Date-a)/1e3,u="ago",l=new Date;if(0===i)return"Just now";if(i>2419200&&58060800>i)return t=l.getMonth()-n.getMonth()+12*(l.getYear()-n.getYear()),1===t?"Last month":t+" months ago";for(;s;){if(i<s[0])return"string"==typeof s[2]?s[1]:Math.floor(i/s[2])+" "+s[1]+" "+u;o++,s=r[o]}return a}function n(e){var n,a,r,o={};for(n=0;n<e.length;n++)a=e[n].cloneNode(!0),r=t(e[n].getAttribute("data-date")),o[r]=o[r]||[],o[r].push(a);return o}function a(t){var n=e.createElement("ul");return n.className="fs_timeline-events",t.forEach(function(e){n.appendChild(e)}),n}function r(t,n){var r=e.createElement("li"),o=e.createElement("span");return r.className="fs_timeline-group",o.className="fs_timeline-subheader",o.appendChild(e.createTextNode(t)),r.appendChild(o),r.appendChild(a(n[t])),r}function o(e,t){var n,a=e.cloneNode(!1),o=!1;Object.keys(t).forEach(function(e){n=r(e,t),o&&(n.className=n.className+"--even"),a.appendChild(n),o=!o}),e.parentNode.replaceChild(a,e)}function s(){var t=e.querySelectorAll("[data-date]"),a=e.querySelector("#list"),r=n(t);o(a,r),a=null}s()}(document);