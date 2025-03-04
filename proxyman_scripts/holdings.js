async function onRequest(context, url, request) {
    if (request.headers["If-None-Match"]) {
        delete request.headers["If-None-Match"]; // не берем кеш, иначе сервер может вернуть 304 Not Modified без данных
    }
    return request;
}

async function onResponse(context, url, request, response) {
    var body = response.body;
    body['query'] = request.queries;
    writeToFile(body, "~/Documents/code/gp2/data.nosync/ww_reports/raw/" + request.queries.q1 + '-' + request.queries.id + '-' + request.queries.offset + '-' + request.queries.order + ".json");
    // q1 - id квартала, id - название фонда, offset - сдвиг при пролистывании страниц, order - порядок сортировки
    return response;
}
