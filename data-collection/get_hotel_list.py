import argparse
from contextlib import nullcontext
import sys
import traceback
from playwright.sync_api import sync_playwright, expect


def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description="Get a list of hotel URLs by locations and an optional limit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    arg_parser.add_argument(
        "locations",
        nargs="+",
        help="List of locations",
    )
    arg_parser.add_argument(
        "--limit", type=int, help="Hotel limit by each location", required=True
    )
    arg_parser.add_argument(
        "--output",
        type=str,
        help="Output file, defaults to console if not specified",
        default="",
    )
    arg_parser.add_argument(
        "--headless",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Whether to run browser in headless mode",
    )
    args = arg_parser.parse_args()

    # Extract values
    locations: list[str] = args.locations
    limit: int = args.limit
    file_name: str = args.output
    is_headless: bool = args.headless

    visited_hotels: set[str] = set()

    with (
        sync_playwright() as p,
        p.chromium.launch(headless=is_headless, timeout=5000) as browser,
        browser.new_context() as context,
        (
            open(file_name, "w", encoding="utf-8")
            if file_name
            else nullcontext(sys.stdout)
        ) as f,
    ):
        hotel_list_page = context.new_page()
        for location in locations:
            processed_hotels: int = 0
            hotel_list_page.goto(
                f"https://google.com/travel/search?q=hotels in {location}&hl=en"
            )
            while processed_hotels < limit:
                loading_circle = (
                    hotel_list_page.locator(".uIOSxc")
                    .nth(0)
                    .get_by_label("Loading results")
                    .nth(0)
                )
                try:
                    expect(loading_circle).not_to_be_in_viewport()
                except AssertionError as e:
                    print(e, file=sys.stderr)
                    break
                hotels_locator = hotel_list_page.locator(".Zvwhrc")
                try:
                    expect(hotels_locator.nth(0)).to_be_visible()
                    expect(
                        hotel_list_page.locator("a.spNMC").nth(0)
                    ).to_be_visible()
                except AssertionError as e:
                    print(e, file=sys.stderr)
                else:
                    for hotel in hotels_locator.all():
                        try:
                            hotel_name = hotel.locator("h2").first.inner_text()
                            if hotel_name in visited_hotels:
                                # The hotel is likely to have been visited
                                continue
                            visited_hotels.add(hotel_name)
                            hotel_link = hotel.locator("a.spNMC").nth(0)
                            expect(hotel_link).to_be_visible(timeout=1000)
                            href = hotel_link.get_attribute("href")
                            if not href:
                                continue
                            if href.startswith("/"):
                                href = "https://google.com" + href
                            f.write(f"{href}\n")
                        except AssertionError as e:
                            # The target location may be not a hotel
                            continue
                        except TimeoutError as e:
                            traceback.print_exc()
                            break
                        processed_hotels += 1
                        if processed_hotels >= limit:
                            break

                if processed_hotels < limit:
                    try:
                        next_page_btn = hotel_list_page.locator(
                            "button[jsname='OCpkoe']"
                        ).first
                        expect(next_page_btn).to_be_visible(timeout=1000)
                        next_page_btn.click()
                    except AssertionError | TimeoutError as e:
                        # Next button may not be found
                        break


if __name__ == "__main__":
    main()
