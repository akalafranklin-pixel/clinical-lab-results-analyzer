import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def abnormality_bar_chart(df: pd.DataFrame):
    status_counts = (
        df["status"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Count")
    )

    fig = px.bar(
        status_counts,
        x="Status",
        y="Count",
        title="Lab Result Status Distribution",
        text="Count"
    )
    return fig


def lab_vs_reference(df: pd.DataFrame):
    """
    Robust visualization of lab values against reference ranges
    """
    df = df.copy()

    # ---- Robust reference range parsing ---- #
    df["ref_low"] = df["reference_range"].str.extract(r"([\d\.]+)").astype(float)
    df["ref_high"] = df["reference_range"].str.extract(r"–\s*([\d\.]+)|-\s*([\d\.]+)") \
        .bfill(axis=1).iloc[:, 0].astype(float)

    # ---- Assign numeric positions for tests ---- #
    df["test_index"] = range(len(df))

    fig = go.Figure()

    # ---- Reference range bands ---- #
    for _, row in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["test_index"], row["test_index"]],
                y=[row["ref_low"], row["ref_high"]],
                mode="lines",
                line=dict(width=8),
                showlegend=False,
                hoverinfo="skip"
            )
        )

    # ---- Actual lab values ---- #
    fig.add_trace(
        go.Scatter(
            x=df["test_index"],
            y=df["value"],
            mode="markers",
            marker=dict(
                size=12,
                symbol="circle"
            ),
            text=df["test"],
            hovertemplate="<b>%{text}</b><br>Value: %{y}<extra></extra>",
            showlegend=False
        )
    )

    fig.update_layout(
        title="Lab Values vs Reference Ranges",
        xaxis=dict(
            tickmode="array",
            tickvals=df["test_index"],
            ticktext=df["test"],
            title="Test"
        ),
        yaxis=dict(title="Value"),
        template="plotly_white"
    )

    return fig
