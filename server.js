/*const express = require("express");
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const archiver = require("archiver");
const axios = require("axios");
const FormData = require("form-data");
const app = express();

const uploadDir = path.join(__dirname, "uploads");
const outputDir = path.join(__dirname, "output");

// Ensure directories exist
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadDir),
    filename: (req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`),
});
const upload = multer({ storage });

// Helper function to delete files safely
const safeDeleteFile = (filePath) => {
    setTimeout(() => {
        fs.unlink(filePath, (err) => {
            if (err) console.error(`Failed to delete ${filePath}:`, err.message);
        });
    }, 500);
};
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "/photo-enhancer.html"));
});
app.post("/process-images", upload.array("images"), async (req, res) => {
    const files = req.files;
    if (!files || files.length === 0) return res.status(400).json({ message: "No files uploaded." });
    
    console.log(`Processing ${files.length} images...`);
    const processedFiles = [];

    for (const file of files) {
        const processedFilePath = path.join(outputDir, `enhanced-${file.filename}`);
        try {
            console.log(`Sending ${file.filename} to Python API...`);
            const formData = new FormData();
            formData.append("image", fs.createReadStream(file.path));
            
            const response = await axios.post("http://127.0.0.1:5000/auto_fix", formData, {
                headers: { ...formData.getHeaders() },
                responseType: "stream",
            });
            
            const writer = fs.createWriteStream(processedFilePath);
            response.data.pipe(writer);
            await new Promise((resolve, reject) => {
                writer.on("finish", resolve);
                writer.on("error", reject);
            });
            
            console.log(`Processed file saved: ${processedFilePath}`);
            processedFiles.push(processedFilePath);
        } catch (error) {
            console.error("Error processing image via Flask API:", error.message);
            return res.status(500).json({ message: "Error processing images." });
        }
    }

    // Zip the processed images
    const zipFileName = `processed-${Date.now()}.zip`;
    const zipFilePath = path.join(outputDir, zipFileName);
    const archive = archiver("zip", { zlib: { level: 9 } });
    const output = fs.createWriteStream(zipFilePath);
    archive.pipe(output);
    
    processedFiles.forEach(file => archive.file(file, { name: path.basename(file) }));
    await archive.finalize();
    
    console.log(`Zip file created: ${zipFilePath}`);
    files.forEach(file => safeDeleteFile(file.path));
    processedFiles.forEach(file => safeDeleteFile(file));

    res.json({ zipUrl: `/output/${zipFileName}` });
});

app.use("/output", express.static(outputDir));
const PORT = 4000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));*/

const express = require("express");
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const archiver = require("archiver");
const axios = require("axios");
const FormData = require("form-data");
const { v2: cloudinary } = require("cloudinary");

const app = express();
const uploadDir = path.join(__dirname, "uploads");
const outputDir = path.join(__dirname, "output");

// Ensure directories exist
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, uploadDir),
    filename: (req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`),
});
const upload = multer({ storage });

// Configure Cloudinary
cloudinary.config({
    cloud_name: 'dy8bgjzqw',
    api_key: '693158269584459',
    api_secret: 'cQXdpUwu0cdLMJs8BD2dWhoKKuo',
  });

// Helper function to delete files safely
const safeDeleteFile = (filePath) => {
    setTimeout(() => {
        fs.unlink(filePath, (err) => {
            if (err) console.error(`Failed to delete ${filePath}:`, err.message);
        });
    }, 500);
};

app.post("/process-images", upload.array("images"), async (req, res) => {
    const files = req.files;
    if (!files || files.length === 0) return res.status(400).json({ message: "No files uploaded." });
    
    console.log(`Processing ${files.length} images...`);
    const processedFiles = [];

    for (const file of files) {
        const processedFilePath = path.join(outputDir, `enhanced-${file.filename}`);
        try {
            console.log(`Sending ${file.filename} to Python API...`);
            const formData = new FormData();
            formData.append("image", fs.createReadStream(file.path));
            
            const response = await axios.post("http://127.0.0.1:5000/auto_fix", formData, {
                headers: { ...formData.getHeaders() },
                responseType: "stream",
            });
            
            const writer = fs.createWriteStream(processedFilePath);
            response.data.pipe(writer);
            await new Promise((resolve, reject) => {
                writer.on("finish", resolve);
                writer.on("error", reject);
            });
            console.log(`Processed file saved: ${processedFilePath}`);

            // Upload to Cloudinary for additional AI enhancements
            console.log(`Uploading ${processedFilePath} to Cloudinary...`);
            const cloudinaryResponse = await cloudinary.uploader.upload(processedFilePath, {
                transformation: [
                   
                   // { effect: "upscale" },
                    { effect: "enhance" },
                    { adjust: "improve" },
                    { color: "blue:20;green:10" } // Adding a slight boost of blue and green
                ]
            });
            console.log(`Cloudinary processing complete: ${cloudinaryResponse.secure_url}`);

            // Download the final image back from Cloudinary
            const finalProcessedPath = path.join(outputDir, `final-${file.filename}`);
            const finalImageResponse = await axios({
                url: cloudinaryResponse.secure_url,
                responseType: "stream",
            });
            const finalWriter = fs.createWriteStream(finalProcessedPath);
            finalImageResponse.data.pipe(finalWriter);
            await new Promise((resolve, reject) => {
                finalWriter.on("finish", resolve);
                finalWriter.on("error", reject);
            });
            
            processedFiles.push(finalProcessedPath);
        } catch (error) {
            console.error("Error processing image:", error.message);
            return res.status(500).json({ message: "Error processing images." });
        }
    }

    // Zip the processed images
    const zipFileName = `processed-${Date.now()}.zip`;
    const zipFilePath = path.join(outputDir, zipFileName);
    const archive = archiver("zip", { zlib: { level: 9 } });
    const output = fs.createWriteStream(zipFilePath);
    archive.pipe(output);
    
    processedFiles.forEach(file => archive.file(file, { name: path.basename(file) }));
    await archive.finalize();
    
    console.log(`Zip file created: ${zipFilePath}`);
    files.forEach(file => safeDeleteFile(file.path));
    processedFiles.forEach(file => safeDeleteFile(file));

    res.json({ zipUrl: `/output/${zipFileName}` });
});

app.use("/output", express.static(outputDir));
const PORT = 4000;
app.listen(PORT, () => console.log(`Server running on http://localhost:${PORT}`));
