# Run and deploy the dashboard

## Run on your computer

1. Install Python 3.10 or newer.
2. Open a terminal in this repository.
3. Install the project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

5. Streamlit opens the interactive dashboard in your browser. The app creates its fictional sample CSV files the first time it runs if they are not already present.

## Publish a public dashboard

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) using the GitHub account that owns this repository.
2. Choose **Create app**.
3. Select this repository, the `main` branch, and `app.py` as the app file.
4. Choose an available app URL and click **Deploy**.
5. After deployment, share the generated `.streamlit.app` URL.

The app reads its code and dependencies from this public GitHub repository. New commits are picked up by Community Cloud.

## Notes

- This portfolio app uses fictional, generated data. Do not replace it with real patient, student or customer personal information in a public deployment.
- The dashboard is a demonstration of analytical workflow and interactive reporting. Review the metric definitions in the app before interpreting results.
