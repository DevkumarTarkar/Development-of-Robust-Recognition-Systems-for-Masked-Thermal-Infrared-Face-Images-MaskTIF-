from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import mimetypes

import requests


# ------------------------------------------
# API configuration
# ------------------------------------------
@dataclass(frozen=True)
class ApiConfig:
    base_url: str = "http://127.0.0.1:5001"
    timeout_s: int = 30


# ------------------------------------------
# print response nicely
# ------------------------------------------
def print_response(
    label: str,
    response: requests.Response
) -> None:

    print("-" * 50)
    print(f"{label.upper()}")

    print(f"Status Code : {response.status_code}")

    try:
        print("Response    :", response.json())
    except Exception:
        print("Response    :", response.text)

    print("-" * 50)
    print()


# ------------------------------------------
# register user
# ------------------------------------------
def register_user(
    cfg: ApiConfig,
    username: str,
    email: str,
    password: str
) -> requests.Response:

    return requests.post(
        f"{cfg.base_url}/register",
        json={
            "username": username,
            "email": email,
            "password": password
        },
        timeout=cfg.timeout_s
    )


# ------------------------------------------
# login user
# ------------------------------------------
def login_user(
    cfg: ApiConfig,
    username: str,
    password: str
) -> tuple[requests.Response, str | None]:

    response = requests.post(
        f"{cfg.base_url}/login",
        json={
            "username": username,
            "password": password
        },
        timeout=cfg.timeout_s
    )

    token = None

    try:
        token = response.json().get(
            "access_token"
        )
    except Exception:
        token = None

    return response, token


# ------------------------------------------
# predict image
# ------------------------------------------
def predict_image(
    cfg: ApiConfig,
    token: str,
    image_path: Path
) -> requests.Response:

    mime_type = (
        mimetypes.guess_type(
            str(image_path)
        )[0]
        or "image/jpeg"
    )

    headers = {
        "Authorization":
        f"Bearer {token}"
    }

    with image_path.open("rb") as file:

        files = {
            "image": (
                image_path.name,
                file,
                mime_type
            )
        }

        return requests.post(
            f"{cfg.base_url}/predict",
            headers=headers,
            files=files,
            timeout=cfg.timeout_s
        )


# ------------------------------------------
# test OPTIONS request
# ------------------------------------------
def options_request(
    cfg: ApiConfig
) -> requests.Response:

    return requests.options(
        f"{cfg.base_url}/predict",
        timeout=cfg.timeout_s
    )


# ------------------------------------------
# command line arguments
# ------------------------------------------
def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Smoke test for "
            "register/login/predict"
        )
    )

    parser.add_argument(
        "--url",
        default="http://127.0.0.1:5001",
        help="API base URL"
    )

    parser.add_argument(
        "--username",
        default="testuser1",
        help="Username"
    )

    parser.add_argument(
        "--email",
        default="test1@test.com",
        help="Email"
    )

    parser.add_argument(
        "--password",
        default="Password1",
        help="Password"
    )

    parser.add_argument(
        "--file",
        default="sample.jpg",
        help="Image path"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout seconds"
    )

    return parser.parse_args()


# ------------------------------------------
# main function
# ------------------------------------------
def main():

    args = parse_args()

    cfg = ApiConfig(
        base_url=args.url,
        timeout_s=args.timeout
    )

    image_path = Path(args.file)

    # register
    print("Testing Register API...")

    register_response = register_user(
        cfg,
        args.username,
        args.email,
        args.password
    )

    print_response(
        "register",
        register_response
    )

    # login
    print("Testing Login API...")

    login_response, token = login_user(
        cfg,
        args.username,
        args.password
    )

    print_response(
        "login",
        login_response
    )

    # predict
    if token and image_path.exists():

        print("Testing Predict API...")

        predict_response = predict_image(
            cfg,
            token,
            image_path
        )

        print_response(
            "predict",
            predict_response
        )

    else:

        print(
            "Skipping prediction "
            "(token/image missing)"
        )

    # options
    print("Testing OPTIONS Request...")

    options_response = options_request(
        cfg
    )

    print_response(
        "options",
        options_response
    )


# ------------------------------------------
# start program
# ------------------------------------------
if __name__ == "__main__":
    main()