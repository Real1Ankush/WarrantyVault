import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [assets, setAssets] = useState([]);

  const [query, setQuery] = useState("");
  const [assistantResult, setAssistantResult] = useState(null);

  const [selectedAsset, setSelectedAsset] = useState(null);
  const [claim, setClaim] = useState(null);

  const [loadingAssets, setLoadingAssets] = useState(true);
  const [loadingAssistant, setLoadingAssistant] = useState(false);
  const [loadingClaim, setLoadingClaim] = useState(false);

  const [showUpload, setShowUpload] = useState(false);
  const [receiptFile, setReceiptFile] = useState(null);
  const [warrantyFile, setWarrantyFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadMessageType, setUploadMessageType] =
    useState("");

  useEffect(() => {
    loadAssets();
  }, []);

  async function loadAssets() {
    try {
      setLoadingAssets(true);

      const response = await fetch(
        `${API_BASE_URL}/api/assets/`
      );

      if (!response.ok) {
        throw new Error("Failed to load assets.");
      }

      const data = await response.json();

      setAssets(data.assets || []);
    } catch (error) {
      console.error("Asset loading error:", error);
    } finally {
      setLoadingAssets(false);
    }
  }

  async function loadClaim(assetId) {
    try {
      setLoadingClaim(true);
      setClaim(null);

      const response = await fetch(
        `${API_BASE_URL}/api/assistant/claim/${assetId}`
      );

      if (!response.ok) {
        throw new Error("Failed to load asset details.");
      }

      const data = await response.json();

      const asset = assets.find(
        (item) => item.id === assetId
      );

      setSelectedAsset(asset || null);
      setClaim(data.claim || null);

      window.scrollTo({
        top: 0,
        behavior: "smooth",
      });
    } catch (error) {
      console.error("Claim loading error:", error);
    } finally {
      setLoadingClaim(false);
    }
  }

  async function askAssistant() {
    if (!query.trim()) {
      return;
    }

    try {
      setLoadingAssistant(true);
      setAssistantResult(null);
      setSelectedAsset(null);
      setClaim(null);

      const response = await fetch(
        `${API_BASE_URL}/api/assistant/query`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            query: query.trim(),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Assistant request failed.");
      }

      const data = await response.json();

      setAssistantResult(data);
    } catch (error) {
      console.error("Assistant error:", error);

      setAssistantResult({
        status: "error",
        message:
          "Could not connect to the warranty assistant.",
      });
    } finally {
      setLoadingAssistant(false);
    }
  }

  async function uploadAsset() {
    if (!receiptFile) {
      setUploadMessageType("error");
      setUploadMessage("Please select a receipt.");
      return;
    }

    try {
      setUploading(true);
      setUploadMessage("");
      setUploadMessageType("");

      const formData = new FormData();

      formData.append("receipt", receiptFile);

      if (warrantyFile) {
        formData.append("warranty", warrantyFile);
      }

      const response = await fetch(
        `${API_BASE_URL}/api/assets/process`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Upload failed."
        );
      }

      // =====================================================
      // DUPLICATE PURCHASE
      // =====================================================

      if (data.already_exists === true) {
        setUploadMessageType("duplicate");
        setUploadMessage(
          `This purchase is already in your wallet (Asset #${data.asset_id}).`
        );

        // Refresh anyway in case the backend data changed.
        await loadAssets();

        return;
      }

      // =====================================================
      // NEW PURCHASE
      // =====================================================

      setUploadMessageType("success");
      setUploadMessage(
        "Purchase added to your wallet successfully."
      );

      setReceiptFile(null);
      setWarrantyFile(null);

      await loadAssets();

      // Close the upload panel after success.
      setTimeout(() => {
        setShowUpload(false);
        setUploadMessage("");
        setUploadMessageType("");
      }, 1800);
    } catch (error) {
      console.error(
        "Upload error:",
        error
      );

      setUploadMessage(
        error.message ||
          "Could not upload purchase."
      );
      setUploadMessageType("error");
    } finally {
      setUploading(false);
    }
  }

  async function deleteAsset(assetId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this asset from your wallet?"
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/assets/${assetId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to delete asset."
        );
      }

      // Clear details if the deleted asset was selected.
      if (selectedAsset?.id === assetId) {
        setSelectedAsset(null);
        setClaim(null);
      }

      // Refresh wallet.
      await loadAssets();

    } catch (error) {
      console.error("Delete asset error:", error);

      window.alert(
        error.message || "Could not delete asset."
      );
    }
  }

  function openInvoice(assetId) {
    window.open(
      `${API_BASE_URL}/api/assets/${assetId}/documents/receipt`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function openDocument(endpoint) {
    if (!endpoint) {
      return;
    }

    window.open(
      `${API_BASE_URL}${endpoint}`,
      "_blank",
      "noopener,noreferrer"
    );
  }

  function getStatusClass(status) {
    if (status === "active") {
      return "status-active";
    }

    if (status === "expired") {
      return "status-expired";
    }

    return "status-unknown";
  }

  function getStatusLabel(status) {
    if (status === "active") {
      return "Active";
    }

    if (status === "expired") {
      return "Expired";
    }

    return "Unknown";
  }

  function getAssetIcon(product) {
    const name = (product || "").toLowerCase();

    if (
      name.includes("headphone") ||
      name.includes("earphone") ||
      name.includes("earbud")
    ) {
      return "🎧";
    }

    if (
      name.includes("racket") ||
      name.includes("badminton")
    ) {
      return "🏸";
    }

    if (
      name.includes("laptop") ||
      name.includes("macbook")
    ) {
      return "💻";
    }

    if (
      name.includes("phone") ||
      name.includes("iphone")
    ) {
      return "📱";
    }

    if (name.includes("camera")) {
      return "📷";
    }

    if (name.includes("tv")) {
      return "📺";
    }

    return "📦";
  }

  function handleCandidateClick(candidate) {
    loadClaim(candidate.id);
  }

  return (
    <div className="app">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <header className="topbar">
        <div>
          <h1>WarrantyVault</h1>

          <p>
            Your digital receipt & warranty wallet
          </p>
        </div>

        <div className="topbar-badge">
          AI Warranty Assistant
        </div>
      </header>


      <main className="container">

        {/* =====================================================
            ASSETS SECTION
        ====================================================== */}

        <section className="section">

          <div className="section-header">

            <div>
              <h2>Your Assets</h2>

              <p>
                Receipts, purchases and warranty information
              </p>
            </div>

            <div className="asset-actions">

              <span className="asset-count">
                {assets.length} assets
              </span>

              <button
                className="add-purchase-button"
                onClick={() => {
                  setShowUpload(!showUpload);
                  setUploadMessage("");
                }}
              >
                + Add Purchase
              </button>

            </div>

          </div>


          {/* =====================================================
              UPLOAD PANEL
          ====================================================== */}

          {showUpload && (
            <div className="upload-panel">

              <div className="upload-header">

                <div>
                  <h3>Add a purchase</h3>

                  <p>
                    Upload your receipt and optionally add
                    a warranty document.
                  </p>
                </div>

                <button
                  className="close-button"
                  onClick={() => {
                    setShowUpload(false);
                    setReceiptFile(null);
                    setWarrantyFile(null);
                    setUploadMessage("");
                  }}
                >
                  ✕
                </button>

              </div>


              <div className="upload-grid">

                {/* RECEIPT */}

                <label className="file-input-card">

                  <span className="file-title">
                    📄 Receipt
                  </span>

                  <span className="file-description">
                    Required
                  </span>

                  <input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(event) =>
                      setReceiptFile(
                        event.target.files?.[0] ||
                          null
                      )
                    }
                  />

                  {receiptFile && (
                    <span className="selected-file">
                      {receiptFile.name}
                    </span>
                  )}

                </label>


                {/* WARRANTY */}

                <label className="file-input-card">

                  <span className="file-title">
                    🛡️ Warranty document
                  </span>

                  <span className="file-description">
                    Optional
                  </span>

                  <input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(event) =>
                      setWarrantyFile(
                        event.target.files?.[0] ||
                          null
                      )
                    }
                  />

                  {warrantyFile && (
                    <span className="selected-file">
                      {warrantyFile.name}
                    </span>
                  )}

                </label>

              </div>


              <div className="upload-footer">

                <button
                  className="save-purchase-button"
                  onClick={uploadAsset}
                  disabled={uploading}
                >
                  {uploading
                    ? "Processing..."
                    : "Save to Wallet"}
                </button>

                {uploadMessage && (
                  <span
                    className={`upload-message ${uploadMessageType}`}
                  >
                    {uploadMessageType === "duplicate" && "⚠️ "}
                    {uploadMessageType === "success" && "✅ "}
                    {uploadMessageType === "error" && "❌ "}
                    {uploadMessage}
                  </span>
                )}

              </div>

            </div>
          )}


          {/* =====================================================
              ASSET LIST
          ====================================================== */}

          {loadingAssets ? (

            <div className="empty-state">
              Loading your assets...
            </div>

          ) : assets.length === 0 ? (

            <div className="empty-state">
              No assets found.
            </div>

          ) : (

            <div className="asset-grid">

              {assets.map((asset) => (

                <div
                  className="asset-card clickable"
                  key={asset.id}
                  onClick={() =>
                    loadClaim(asset.id)
                  }
                >

                  <div className="asset-icon">
                    {getAssetIcon(
                      asset.product
                    )}
                  </div>


                  <div className="asset-info">

                    <h3>{asset.product}</h3>

                    <p className="seller">
                      {asset.seller}
                    </p>


                    <div className="asset-details">

                      <span>
                        Purchased:{" "}
                        {asset.purchase_date ||
                          "Unknown"}
                      </span>

                      <span>
                        ₹
                        {asset.total_amount ??
                          "—"}
                      </span>

                    </div>


                    <div className="asset-footer">

                      <span
                        className={`status ${getStatusClass(
                          asset.warranty_status
                        )}`}
                      >
                        Warranty:{" "}
                        {getStatusLabel(
                          asset.warranty_status
                        )}
                      </span>


                      <div className="asset-buttons">

                        <button
                          className="invoice-button"
                          onClick={(event) => {
                            event.stopPropagation();
                            openInvoice(asset.id);
                          }}
                        >
                          📄 View Invoice
                        </button>

                        <button
                          className="delete-button"
                          onClick={(event) => {
                            event.stopPropagation();
                            deleteAsset(asset.id);
                          }}
                        >
                          🗑 Delete
                        </button>

                      </div>

                    </div>

                  </div>

                </div>
              ))}

            </div>
          )}

        </section>


        {/* =====================================================
            ASSET DETAILS
        ====================================================== */}

        {(selectedAsset || claim) && (

          <section className="details-section">

            <div className="details-header">

              <div>

                <span className="details-label">
                  Asset details
                </span>

                <h2>
                  {claim?.product?.name ||
                    selectedAsset?.product ||
                    "Asset"}
                </h2>

              </div>


              <button
                className="close-button"
                onClick={() => {
                  setSelectedAsset(null);
                  setClaim(null);
                }}
              >
                ✕
              </button>

            </div>


            {loadingClaim ? (

              <div className="empty-state">
                Loading asset details...
              </div>

            ) : claim ? (

              <div className="details-content">

                {/* DETAILS */}

                <div className="claim-grid">

                  <div className="detail-box">
                    <span>Product ID</span>

                    <strong>
                      {claim.product?.product_id ||
                        "—"}
                    </strong>
                  </div>


                  <div className="detail-box">
                    <span>Seller</span>

                    <strong>
                      {claim.product?.seller ||
                        "—"}
                    </strong>
                  </div>


                  <div className="detail-box">
                    <span>Purchase Date</span>

                    <strong>
                      {claim.purchase?.purchase_date ||
                        "—"}
                    </strong>
                  </div>


                  <div className="detail-box">
                    <span>Invoice Number</span>

                    <strong>
                      {claim.purchase
                        ?.invoice_number || "—"}
                    </strong>
                  </div>


                  <div className="detail-box">
                    <span>Amount</span>

                    <strong>
                      ₹
                      {claim.purchase?.amount ??
                        "—"}
                    </strong>
                  </div>


                  <div className="detail-box">

                    <span>Warranty</span>

                    <strong
                      className={`status ${getStatusClass(
                        claim.warranty?.status
                      )}`}
                    >
                      {getStatusLabel(
                        claim.warranty?.status
                      )}
                    </strong>

                  </div>

                </div>


                {/* WARRANTY */}

                <div className="warranty-summary">

                  <h3>
                    Warranty information
                  </h3>

                  <p>
                    {claim.warranty?.message}
                  </p>


                  {claim.warranty?.months != null && (
                    <p>
                      Warranty period:{" "}
                      <strong>
                        {claim.warranty.months}{" "}
                        months
                      </strong>
                    </p>
                  )}


                  {claim.warranty?.expiry && (
                    <p>
                      Warranty expiry:{" "}
                      <strong>
                        {claim.warranty.expiry}
                      </strong>
                    </p>
                  )}

                </div>


                {/* DOCUMENTS */}

                <div className="documents">

                  <h3>Documents</h3>


                  {claim.documents?.length ? (

                    <div className="document-list">

                      {claim.documents.map(
                        (document) => {

                          if (
                            document.status !==
                            "available"
                          ) {
                            return (
                              <div
                                className="document-missing"
                                key={
                                  document.type
                                }
                              >
                                {document.type ===
                                "receipt"
                                  ? "📄"
                                  : "🛡️"}{" "}
                                {document.type}:
                                Missing
                              </div>
                            );
                          }


                          return (
                            <button
                              key={
                                document.document_id
                              }
                              className="document-card"
                              onClick={() =>
                                openDocument(
                                  document.endpoint
                                )
                              }
                            >
                              <span>
                                📄{" "}
                                {document.filename}
                              </span>

                              <span>
                                Open →
                              </span>
                            </button>
                          );
                        }
                      )}

                    </div>

                  ) : (

                    <p className="muted">
                      No documents available.
                    </p>

                  )}

                </div>


                {/* NEXT STEPS */}

                <div className="next-steps">

                  <h3>
                    Next steps
                  </h3>

                  <ul>

                    {claim.next_steps?.map(
                      (step, index) => (
                        <li key={index}>
                          {step}
                        </li>
                      )
                    )}

                  </ul>

                </div>

              </div>

            ) : null}

          </section>

        )}


        {/* =====================================================
            ASSISTANT
        ====================================================== */}

        <section className="assistant-section">

          <div className="assistant-header">

            <div className="assistant-icon">
              ✨
            </div>

            <div>

              <h2>
                Ask your warranty assistant
              </h2>

              <p>
                Describe the product or problem
                in natural language.
              </p>

            </div>

          </div>


          <div className="query-box">

            <input
              type="text"
              placeholder="My headphones stopped working..."
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  askAssistant();
                }
              }}
            />


            <button
              onClick={askAssistant}
              disabled={loadingAssistant}
            >
              {loadingAssistant
                ? "Thinking..."
                : "Ask Assistant"}
            </button>

          </div>


          {assistantResult && (

            <div className="assistant-result">

              <div className="result-status">

                {assistantResult.status ===
                "matched"
                  ? "✅ Match found"
                  : assistantResult.status ===
                    "ambiguous"
                  ? "🔎 Multiple matches"
                  : assistantResult.status ===
                    "not_found"
                  ? "❌ No match"
                  : "ℹ️ Assistant"}

              </div>


              <h3>
                {assistantResult.message}
              </h3>


              {/* MULTIPLE CANDIDATES */}

              {assistantResult.candidates &&
                assistantResult.candidates.length > 0 && (

                  <div className="candidate-list">

                    {assistantResult.candidates.map(
                      (candidate) => (

                        <button
                          className="candidate-card clickable-candidate"
                          key={candidate.id}
                          onClick={() =>
                            handleCandidateClick(
                              candidate
                            )
                          }
                        >

                          <div>

                            <strong>
                              {candidate.product}
                            </strong>

                            <p>
                              Purchased:{" "}
                              {candidate.purchase_date ||
                                "Unknown"}
                            </p>

                          </div>


                          <div className="candidate-right">

                            <span
                              className={`status ${getStatusClass(
                                candidate.warranty_status
                              )}`}
                            >
                              {getStatusLabel(
                                candidate.warranty_status
                              )}
                            </span>

                            <span className="arrow">
                              →
                            </span>

                          </div>

                        </button>
                      )
                    )}

                  </div>
                )}


              {/* AUTOMATIC CLAIM */}

              {assistantResult.claim && (

                <div className="claim-card">

                  <div className="claim-header">

                    <h3>
                      Warranty claim information
                    </h3>

                    <span
                      className={`status ${getStatusClass(
                        assistantResult.claim
                          .warranty?.status
                      )}`}
                    >
                      {getStatusLabel(
                        assistantResult.claim
                          .warranty?.status
                      )}
                    </span>

                  </div>


                  <div className="claim-grid">

                    <div>
                      <span>Product</span>

                      <strong>
                        {
                          assistantResult.claim
                            .product?.name
                        }
                      </strong>
                    </div>


                    <div>
                      <span>Purchase date</span>

                      <strong>
                        {
                          assistantResult.claim
                            .purchase?.purchase_date
                        }
                      </strong>
                    </div>


                    <div>
                      <span>Invoice</span>

                      <strong>
                        {
                          assistantResult.claim
                            .purchase?.invoice_number
                        }
                      </strong>
                    </div>

                  </div>


                  {assistantResult.claim.documents
                    ?.length > 0 && (

                    <div className="documents">

                      <h4>
                        Available documents
                      </h4>

                      {assistantResult.claim.documents.map(
                        (document) => (

                          document.status ===
                          "available" ? (

                            <button
                              key={
                                document.document_id
                              }
                              className="document-link"
                              onClick={() =>
                                openDocument(
                                  document.endpoint
                                )
                              }
                            >
                              📄{" "}
                              {document.filename}
                            </button>

                          ) : null

                        )
                      )}

                    </div>

                  )}


                  <div className="next-steps">

                    <h4>
                      Next steps
                    </h4>

                    <ul>

                      {assistantResult.claim.next_steps?.map(
                        (step, index) => (
                          <li key={index}>
                            {step}
                          </li>
                        )
                      )}

                    </ul>

                  </div>

                </div>

              )}

            </div>
          )}

        </section>

      </main>

    </div>
  );
}

export default App;
