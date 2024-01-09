import argparse
import datetime
import sys
import time
from typing import Generator

from playwright.sync_api import (
    sync_playwright,
    expect,
    Locator,
    Page,
)

from review import Review
from review.writer import ReviewCsvWriter


def is_crawlable_panel(panel: Locator) -> bool:
    """
    Verifies if the comment section is crawlable or not.
    Crawable here means it is not empty and does not contain "Read more" button
    """
    if len(panel.inner_text()) == 0:
        return False
    readmore_buttons = panel.get_by_role("button").all()
    return len(readmore_buttons) == 0


def get_review_from_panel(panel: Locator, hotel_name: str) -> Review | None:
    r = Review(hotel_name=hotel_name)

    review_time_str = panel.locator("span.iUtr1").first.inner_text().strip()
    # print(f"Review was made {review_time_str}")
    if "Google" not in review_time_str:
        print("Warning: Review was not made on Google, skipping")
        return None

    # Based on this solution on StackOverflow: https://stackoverflow.com/a/12566244
    amount_str, fmt = review_time_str.split()[:2]

    amount = float(amount_str.replace("an", "1").replace("a", "1"))
    if amount == 1:
        fmt = (
            fmt.replace("second", "seconds")
            .replace("minute", "minutes")
            .replace("hour", "hours")
            .replace("day", "days")
            .replace("week", "weeks")
            .replace("month", "months")
            .replace("year", "years")
        )

    match fmt:
        case "seconds" | "minutes" | "hours" | "days" | "weeks":
            pass
        case "months":
            amount *= 30.0
            fmt = "days"
        case "years":
            amount *= 365.0
            fmt = "days"
        case _:
            amount = 0
            fmt = "seconds"

    dt = datetime.timedelta(**dict([(fmt, amount)]))
    r.review_timestamp = datetime.datetime.now() - dt

    review_text_elems = panel.locator(".K7oBsc").all()
    for elem in review_text_elems:
        if len(elem.get_by_role("button").all()):
            continue
        review_text = elem.inner_text().strip()
        if not len(review_text):
            continue
        r.review_text = review_text
        break

    rating = panel.locator(".GDWaad").first.inner_text()
    r.rating = float(rating.split("/")[0])

    # Note that trip details is optional
    trip_details_locators = panel.locator(".ThUm5b>span").all()

    if trip_details_locators:
        trip_details = trip_details_locators[0].inner_text().split()
        for detail in trip_details:
            match detail:
                case "Business" | "Vacation":
                    r.trip_type = detail
                case "Family" | "Friends" | "Couple" | "Solo":
                    r.trip_companions = detail

    return r


# TODO: Choose review source from Google only to reduce clutter by other review providers
def get_reviews(
    hotel_page: Page, limit: int
) -> Generator[list[Review], None, None]:
    hotel_name: str = hotel_page.locator("h1.FNkAEc.o4k8l").first.inner_text()
    hotel_page.locator("#reviews>span").first.click()
    processed_reviews: int = 0
    recorded_reviews: int = 0

    while True:
        review_panels_locator = hotel_page.locator(".Svr5cf")

        try:
            hotel_page.keyboard.press("End", delay=1000)
            hotel_page.keyboard.press("PageUp", delay=500)

            try:
                # Maybe we have looked over all reviews
                expect(
                    review_panels_locator.nth(processed_reviews)
                ).to_be_visible(timeout=10000)
            except AssertionError as e:
                print("No more reviews (maybe)")
                print(e)
                return

            review_panels = review_panels_locator.all()[processed_reviews:]
            if len(review_panels) == 0:
                print("No more reviews")
                return
            print(f"Found {len(review_panels)} new review(s)")

            all_reviews: list[Review | None] = [
                get_review_from_panel(panel, hotel_name)
                for panel in review_panels
            ]
            reviews = [review for review in all_reviews if review is not None]
            recorded_reviews += len(reviews)
            # print(f"Yielding {len(reviews)} review(s)")
            yield reviews

            processed_reviews += len(review_panels)
            # print(f"Processed {processed_reviews} review(s)")
            # print(f"Recorded {recorded_reviews} review(s)")
            print("---")

            if recorded_reviews >= limit:
                # print("Reached review count limit, stopping.")
                return
        except AssertionError as e:
            print(e)
            return


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Get hotel reviews from a list of URLs from Google Travel",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_parser.add_argument(
        "input",
        type=str,
        help="Path to file containing hotel URLs",
    )
    arg_parser.add_argument(
        "--output",
        type=str,
        help="Path to output file, defaults to file containing current time",
        default=f"output/hotel-details-{int(time.time() * 1000)}.csv",
    )
    arg_parser.add_argument(
        "--limit", type=int, help="Reviews limit by each hotel", required=True
    )
    arg_parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether to run browser in headless mode",
    )

    args = arg_parser.parse_args()

    input_filename: str = args.input
    output_filename: str = args.output
    limit: int = args.limit
    is_headless: bool = args.headless

    print(f"Running in headless mode: {is_headless}", file=sys.stderr)
    print(f"Reading from {input_filename}", file=sys.stderr)
    print(f"Writing to {output_filename}", file=sys.stderr)

    with (
        sync_playwright() as p,
        p.chromium.launch(headless=is_headless) as browser,
        browser.new_context() as context,
        open(input_filename, "r", encoding="utf-8") as input_file,
        ReviewCsvWriter(output_filename) as writer,
    ):
        hotel_page = context.new_page()
        for line_number, link in enumerate(input_file):
            try:
                hotel_page.goto(link)
                for reviews in get_reviews(hotel_page, limit):
                    writer.append(reviews)
                print(f"Processed {line_number + 1} hotels\n")
            except Exception as e:
                print(e)
                continue


if __name__ == "__main__":
    main()
