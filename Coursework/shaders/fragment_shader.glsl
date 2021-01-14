#version 130					// required to use the OpenGL core standard

// This code was adapted from a tutorial on how to build Fur Effects, written on the website
// xbdev.net. (https://xbdev.net/directx3dx/specialX/Fur/)

//=== in attributes are read from the vertex array, one row per instance of the shader
in vec2 frag_TexCoord;			// the texture coordinates which is coming in from the vertex_shader

//=== Uniforms
uniform float UVScale;			// Fur texture alpha coords are stretched/shrunk, UVScale deals with this
uniform float num_of_layers;	// The number of layers which are to be rendered
uniform float current_layer;		// The current layer which is being rendered
uniform sampler2D textureUnit0;	// The texture being generated from the createFurTextures function
uniform sampler2D textureUnit1;	// The texture which was given for the program.

//=== out attributes
out vec4 outColor;				// The output of the shader will be the colour of the vertex

vec4 furColor;					// 4D vector as there is a RGBA (alpha)
vec4 baseColor = texture(textureUnit1, frag_TexCoord);

//=== main shader code
void main(void) {
	if(current_layer > 0)
	{
		furColor = texture(textureUnit0, frag_TexCoord);
		// If the alpha value is less than 0.1, it isn't used, therefore transparent.
		if(furColor.a < 0.1) discard;

		// If the alpha value is greater than 0.1, then the RGB values are looked at.
		if(furColor.r < 0.1) discard;
		else furColor.r = baseColor.r;
		if(furColor.g < 0.1) discard;
		else furColor.g = baseColor.g;
		if(furColor.b < 0.1) discard;
		else furColor.b = baseColor.b;
	}

	furColor.w = UVScale;


	outColor = furColor;	// Output
	if(current_layer == 0) outColor = vec4(0.0,0.0,0.0,1.0); //sets the base layer to be black with alpha = 1
}
