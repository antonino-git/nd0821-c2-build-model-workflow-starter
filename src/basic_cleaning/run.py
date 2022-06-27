#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    logging.info(f"Downloading input file:{args.input_artifact}")
    input_artifact = run.use_artifact(args.input_artifact)
    input_artifact_path = input_artifact.file()

    df = pd.read_csv(input_artifact_path)

    logging.info(
        f"Remove samples outside the range {args.min_price} - {args.max_price}")
    idx = df['price'].between(args.min_price, args.max_price)
    df = df[idx].copy()

    logging.info(f'Convert last_review field to datatime')
    df['last_review'] = pd.to_datetime(df['last_review'])

    logging.info('Remove rows outside the boundries')

    idx = df['longitude'].between(-74.25, -
                                  73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    df.to_csv('clean_sample.csv', index=False)

    logging.info(f'Upload dataset after basic data cleaning')

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help='Insert the name of the input artifact',
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help='Insert the name of the output artifact',
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help='Insert the type of the output artifact',
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help='Insert a description of the output artifact',
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help='Insert the minimum price of the property to consider. Date releated to property with lower price will be removed',
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help='Insert the maximum price of the property to consider. Date releated to property with higher price will be removed',
        required=True
    )

    args = parser.parse_args()

    go(args)
