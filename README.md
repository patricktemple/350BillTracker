# NY Climate Legislation

## Running locally

From repo root:
```bash
script/run
```

This builds the frontend and then hosts that inside the Flask app, which it starts in a Dockerized environment. Then you can
just hit `http://localhost` to run the frontend.

For local frontend development, you'll want a React dev server instead:
```bash
cd frontend
yarn start
```

This will point to the locally running Flask backend. You can have both running at the same time; just remember
that port 3000 is the live frontend dev server whereas port 80 is the React app built into the Flask backend.

## Deploying

From repo root:
```bash
script/deploy
```