(function (window) {
  function detectApiBase() {
    if (window.location.protocol === "file:") return "http://localhost:5000";
    var port = window.location.port || "";
    if (port === "8080" || port === "8088" || port === "80" || port === "") return "";
    return "http://localhost:5000";
  }

  var apiBase = window.API_BASE_URL || detectApiBase();
  window.API_BASE_URL = apiBase;

  window.apiUrl = function apiUrl(path) {
    var raw = String(path || "");
    if (/^https?:\/\//i.test(raw)) {
      try {
        var url = new URL(raw);
        if (url.hostname === "localhost" && url.port === "5000") {
          return apiBase + url.pathname + url.search + url.hash;
        }
      } catch (e) {
        return raw;
      }
      return raw;
    }

    if (!raw.startsWith("/")) raw = "/" + raw;
    return apiBase + raw;
  };

  function isApiRequest(original, rewritten) {
    var raw = String(original || "");
    if (raw.startsWith("/") || raw.startsWith("http://localhost:5000")) return true;
    try {
      var url = new URL(String(rewritten), window.location.origin);
      if (apiBase === "" && url.origin === window.location.origin) return true;
      if (apiBase !== "") {
        var apiOrigin = new URL(apiBase, window.location.origin).origin;
        return url.origin === apiOrigin;
      }
    } catch (e) {
      return false;
    }
    return false;
  }

  var nativeFetch = window.fetch.bind(window);
  window.fetch = function fetchWithApiDefaults(input, options) {
    var init = options || {};
    var originalUrl = input instanceof Request ? input.url : String(input);
    var rewrittenUrl = window.apiUrl(originalUrl);
    var token = window.localStorage && window.localStorage.getItem("access_token");

    if (token && isApiRequest(originalUrl, rewrittenUrl)) {
      var headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined));
      if (!headers.has("Authorization")) {
        headers.set("Authorization", "Bearer " + token);
      }
      init = Object.assign({}, init, { headers: headers });
    }

    return nativeFetch(rewrittenUrl, init);
  };
})(window);
