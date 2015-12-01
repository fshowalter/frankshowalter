(function app() {
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

  var timestamps = document.querySelectorAll('[data-time-ago]');

  for (var i = 0; i < timestamps.length; i++) {
    timestamps[i].innerText = timeAgo(timestamps[i].getAttribute('data-time-ago'))
  }
})();