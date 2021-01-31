# Financial Resilience Modeller

Interface to a compound agent-based model focused on examining hypothetical scenarios for the purpose of speculative analysis. Of interest is the propagation of alternative shocks across each inner model (pandemic, financial), where the former propagates a shock in the form of virulent spread and the latter propagates a shock in the form of reduced capacity for financial lending.

## Example Simulation

![.gif of Pandemic model](Static/example_simulation/pandemic.gif)

## GUI Instructions

![Information on GUI components](Static/user_guide.png)

### Environment Configuration

The virtual environment has been configured using [Poetry](https://python-poetry.org/docs/cli/), the modern solution for package/environment management. Please adhere to its docs when adding/removing/maintaining packages.

#### Operating System

This program will function as intended on Darwin OS alone.

#### Development Commands

```bash
poetry shell
poetry install
poetry run python Application/GUI.py
```

#### House-keeping Commands

```bash
poetry run black Application/*
poetry run pylint Application/*
poetry run pyinstaller --onefile --noconfirm --noconsole --clean PyI.spec
```

##### WARNING: Bokeh Plotting

As of v.2.0.0+, Bokeh has replaced PhantomJS when generating PNG exports. Bokeh now uses Selenium for the purpose of headless browser-ing within which the JavaScript-based plots can be rendered. This requires a Chromium or Firefox-based browser to be installed on the user's system. This program will attempt to first utilise Chromium and grab the corresponding web driver version to to what is installed locally, and failing that, the same process will be attempted with Firefox.

**tl;dr:** Install a Chromium or Firefox-based browser to use this program.
