async function onRequest(context, url, request) {
    if (request.headers["If-None-Match"]) {
        delete request.headers["If-None-Match"]; // не берем кеш, иначе сервер может вернуть 304 Not Modified без данных
    }
    return request;
}

async function onResponse(context, url, request, response) {
    var body = response.body;
    writeToFile(body, "~/Documents/code/gp2/data.nosync/stock_prices/" + request.queries.stock_id + ".json");
    return response;
}
