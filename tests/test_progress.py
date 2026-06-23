from bson import ObjectId

from api.progress import compute_progress


TODO = {"id": "s1", "name": "Todo", "color": "323232", "order": 1}
DOING = {"id": "s2", "name": "In-Progress", "color": "EFA610", "order": 2}
DONE = {"id": "s3", "name": "Done", "color": "01796E", "order": 3}


def test_no_tasks_is_zero_percent_and_never_divides_by_zero():
    result = compute_progress([TODO, DONE], [])

    assert result["total"] == 0
    assert result["done"] == 0
    assert result["completeness"] == 0.0
    assert [segment["count"] for segment in result["segments"]] == [0, 0]


def test_completeness_is_done_column_over_total():
    result = compute_progress([TODO, DOING, DONE], ["s1", "s1", "s2", "s3"])

    assert result["total"] == 4
    assert result["done"] == 1
    assert result["completeness"] == 0.25
    assert [segment["count"] for segment in result["segments"]] == [2, 1, 1]


def test_all_done_is_one_hundred_percent():
    result = compute_progress([TODO, DONE], ["s3", "s3"])

    assert result["completeness"] == 1.0
    assert result["done"] == result["total"] == 2


def test_done_is_the_highest_order_status_not_the_last_listed():
    result = compute_progress([DONE, TODO], ["s3", "s1"])

    assert result["done"] == 1
    assert result["completeness"] == 0.5


def test_unknown_and_missing_status_counts_toward_total_in_leftmost_column():
    result = compute_progress([TODO, DONE], [None, "ghost", "s3"])

    assert result["total"] == 3
    assert result["done"] == 1
    assert result["segments"][0]["count"] == 2
    assert result["segments"][1]["count"] == 1


def test_segments_preserve_status_order_color_and_fraction():
    result = compute_progress([DONE, TODO, DOING], ["s1", "s3"])
    names = [segment["name"] for segment in result["segments"]]
    colors = [segment["color"] for segment in result["segments"]]

    assert names == ["Todo", "In-Progress", "Done"]
    assert colors == ["323232", "EFA610", "01796E"]
    assert result["segments"][0]["fraction"] == 0.5
    assert result["segments"][2]["fraction"] == 0.5


def test_handles_real_objectid_statuses_and_tasks():
    todo_id, done_id = ObjectId(), ObjectId()
    statuses = [
        {"id": todo_id, "name": "Todo", "color": "323232", "order": 1},
        {"id": done_id, "name": "Done", "color": "01796e", "order": 2},
    ]
    result = compute_progress(statuses, [todo_id, done_id, done_id, None])

    assert result["total"] == 4
    assert result["done"] == 2
    assert result["completeness"] == 0.5
    assert result["segments"][0]["count"] == 2
    assert result["segments"][1]["count"] == 2


def test_duplicate_order_resolves_deterministically_regardless_of_input_order():
    a = {"id": "a", "name": "A", "color": "111111", "order": 1}
    b = {"id": "b", "name": "B", "color": "222222", "order": 1}

    forward = compute_progress([a, b], ["b"])
    reversed_ = compute_progress([b, a], ["b"])

    assert [segment["name"] for segment in forward["segments"]] == ["A", "B"]
    assert [segment["name"] for segment in reversed_["segments"]] == ["A", "B"]

