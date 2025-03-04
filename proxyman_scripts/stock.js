async function onRequest(context, url, request) {
    if (request.headers["If-None-Match"]) {
        delete request.headers["If-None-Match"]; // не берем кеш, иначе сервер может вернуть 304 Not Modified без данных
    }
    return request;
}

async function onResponse(context, url, request, response) {
    var body = response.body;
    writeToFile(body, "~/Documents/code/gp2/data.nosync/stock_pages/" + url.match(/https:\/\/whalewisdom\.com\/stock\/([^?]*)/)[1].replace(/\//g, '_b_') + ".html");
    // парсим id акции из url'a формата https://whalewisdom.com/stock/get_current_chart_data?stock_id=163015
    return response;
}
