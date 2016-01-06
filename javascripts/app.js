(
  function(document) {
    function timeAgo(date){
      var units = [
        { name: "second", limit: 60, in_seconds: 1 },
        { name: "minute", limit: 3600, in_seconds: 60 },
        { name: "hour", limit: 86400, in_seconds: 3600  },
        { name: "day", limit: 604800, in_seconds: 86400 },
        { name: "week", limit: 2629743, in_seconds: 604800  },
        { name: "month", limit: 31556926, in_seconds: 2629743 },
        { name: "year", limit: null, in_seconds: 31556926 }
      ];
      var diff = (new Date() - new Date(date)) / 1000;
      if (diff < 5) return "now";

      var i = 0, unit;
      while (unit = units[i++]) {
        if (diff < unit.limit || !unit.limit){
          var diff =  Math.floor(diff / unit.in_seconds);
          return diff + " " + unit.name + (diff>1 ? "s" : "") + ' ago';
        }
      };
    }

    function getOrdinal(n) {
      var s=['th', 'st', 'nd', 'rd'];
      var v=n%100;

      return n+(s[(v-20)%10]||s[v]||s[0]);
    }

    var items = document.querySelectorAll('[data-date]');
    var list = document.querySelector('#list');
    var itemsByDate = {};
    var newItem;
    var newHeading;
    var newLink;
    var newSlug;
    var newText;
    var timeInWords;
    var timeItem;

    var months = [
      'January',
      'Februrary',
      'March',
      'April',
      'May',
      'June',
      'July',
      'August',
      'September',
      'October',
      'November',
      'December',
    ];

    for (var i = 0; i < items.length; i++) {
      newItem = document.createElement('li');
      newItem.className = 'event';
      newHeading = document.createElement('h3');
      newHeading.className = "events-heading"
      newLink = document.createElement('a');
      newLink.href = items[i].getAttribute('data-link');
      newLink.appendChild(document.createTextNode(items[i].getAttribute('data-title')));

      newHeading.appendChild(newLink);

      newSlug = document.createElement('p');
      newSlug.className = 'event-slug';
      newSlug.appendChild(document.createTextNode(
        (months[new Date(items[i].getAttribute('data-date')).getMonth()]) + ' ' + getOrdinal(new Date(items[i].getAttribute('data-date')).getDate()) + ' on ' + items[i].getAttribute('data-location')))

      newItem.appendChild(newHeading);
      newItem.appendChild(newSlug);

      timeInWords = timeAgo(items[i].getAttribute('data-date'))
      itemsByDate[timeInWords] = itemsByDate[timeInWords] || [];
      itemsByDate[timeInWords].push(newItem);
    }

    items = null;
    var cNode = list.cloneNode(false);
    var currentTimeAgo;
    var newList;

    Object.keys(itemsByDate).forEach(function(key) {
      var newItem = document.createElement('li');
      newItem.className = 'timeline-time';
      timeItem = document.createElement('span');
      timeItem.className = 'time';
      timeItem.appendChild(document.createTextNode(key));
      newItem.appendChild(timeItem);
      newList = document.createElement('ul');
      newList.className = 'events'

      itemsByDate[key].forEach(function(item) {
        newList.appendChild(item);
      });

      newItem.appendChild(newList);
      cNode.appendChild(newItem);
    });


    list.parentNode.replaceChild(cNode, list);

    list = null;
  }
)(document);
